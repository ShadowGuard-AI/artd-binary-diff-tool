#!/usr/bin/env python3

import argparse
import lief
import capstone
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description="Compares two binary files and highlights the differences in their assembly code.")
    parser.add_argument("file1", help="The first binary file to compare.")
    parser.add_argument("file2", help="The second binary file to compare.")
    parser.add_argument("-a", "--architecture", choices=['x86', 'x64', 'arm', 'arm64'], default='x86',
                        help="The architecture of the binary files (default: x86).")
    parser.add_argument("-o", "--output", help="Output file to save the diff results. If not provided, prints to console.", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    return parser

def _is_executable_section(section):
    """True when lief marks this section as executable code.

    The original call, section.has_characteristic(ELF.SECTION_FLAGS...),
    names an API current lief builds do not have, so every real binary
    failed here. What this lief exposes depends on the format: ELF
    sections carry a flags_list with an EXECINSTR entry, PE sections
    carry a characteristics bitmask with MEM_EXECUTE (0x20000000).
    """
    flags_list = getattr(section, "flags_list", None)
    if flags_list is not None:
        return any(str(flag).endswith("EXECINSTR") for flag in flags_list)
    characteristics = getattr(section, "characteristics", None)
    if characteristics is not None:
        return bool(characteristics & 0x20000000)
    return bool(getattr(section, "flags", 0) & 0x4)


def disassemble(file_path, arch):
    """
    Disassembles a binary file using LIEF and Capstone.

    Args:
        file_path (str): The path to the binary file.
        arch (str): The architecture of the binary ("x86", "x64", "arm", "arm64").

    Returns:
        dict: A dictionary where keys are addresses and values are assembly instructions.
              Returns None on error.
    """
    # Current lief builds raise lief.exception subclasses whose names have
    # moved between releases, so this catches Exception rather than naming
    # one spelling that a newer lief may not have at all.
    try:
        binary = lief.parse(file_path)
        if binary is None:
            logging.error(f"Failed to parse {file_path} with LIEF.")
            return None

        if arch == 'x86':
            md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        elif arch == 'x64':
            md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        elif arch == 'arm':
            md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_ARM)
        elif arch == 'arm64':
            md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        else:
            logging.error(f"Unsupported architecture: {arch}")
            return None

        disassembly = {}
        for section in binary.sections:
            if _is_executable_section(section):
                logging.info(f"Disassembling section: {section.name}")
                # Capstone is run as one linear sweep from the section
                # start. Data embedded in a code section desyncs the
                # sweep, and the iterator simply stops at the first
                # bytes it cannot decode, so the tail of such a section
                # is missing from the result with no sign of the gap.
                # Two sections sharing an address range would also
                # overwrite each other in this dict.
                for i in md.disasm(section.content, section.virtual_address):
                    disassembly[i.address] = i.mnemonic + " " + i.op_str

        return disassembly

    except Exception as e:
        logging.error(f"Error disassembling {file_path}: {e}")
        return None


def diff_assemblies(assembly1, assembly2):
    """
    Compares two disassembled binaries and identifies differences.

    Args:
        assembly1 (dict): The disassembly of the first binary.
        assembly2 (dict): The disassembly of the second binary.

    Returns:
        dict: A dictionary containing the differences between the two assemblies.
              Keys: 'added', 'removed', 'modified'
    """
    # The comparison is keyed on absolute addresses, with no attempt
    # to align the two instruction streams. One instruction inserted
    # early in a function shifts every later address in the second
    # binary, so a one line change can read as hundreds of removed and
    # added instructions rather than one modified spot. This diff is
    # honest for binaries built to load at the same addresses with
    # stable layouts, and mostly noise when they were not.
    added = {}
    removed = {}
    modified = {}

    for addr, instruction in assembly2.items():
        if addr not in assembly1:
            added[addr] = instruction

    for addr, instruction in assembly1.items():
        if addr not in assembly2:
            removed[addr] = instruction
        elif assembly2[addr] != instruction:
            modified[addr] = (instruction, assembly2[addr])  # (original, modified)

    return {'added': added, 'removed': removed, 'modified': modified}


def validate_file(file_path):
    """
    Validates if the provided file path exists and is a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    if not os.path.exists(file_path):
        logging.error(f"Error: File not found: {file_path}")
        return False
    if not os.path.isfile(file_path):
        logging.error(f"Error: Not a file: {file_path}")
        return False
    return True


def write_diff_to_file(diff, output_file):
    # Returns False on a failed write so main can exit 1. Before, the error
    # was only logged and the run still reported completion.
    """
    Writes the disassembly differences to a file.

    Args:
        diff (dict): The dictionary of differences.
        output_file (str): The path to the output file.
    """
    try:
        with open(output_file, "w") as f:
            f.write("Added instructions:\n")
            for addr, instruction in diff['added'].items():
                f.write(f"  0x{addr:x}: {instruction}\n")

            f.write("\nRemoved instructions:\n")
            for addr, instruction in diff['removed'].items():
                f.write(f"  0x{addr:x}: {instruction}\n")

            f.write("\nModified instructions:\n")
            for addr, (original, modified) in diff['modified'].items():
                f.write(f"  0x{addr:x}: Original: {original} | Modified: {modified}\n")

        logging.info(f"Diff written to {output_file}")
        return True
    except Exception as e:
        logging.error(f"Error writing diff to file: {e}")
        return False


def print_diff_to_console(diff):
    """
    Prints the disassembly differences to the console.

    Args:
        diff (dict): The dictionary of differences.
    """
    print("Added instructions:")
    for addr, instruction in diff['added'].items():
        print(f"  0x{addr:x}: {instruction}")

    print("\nRemoved instructions:")
    for addr, instruction in diff['removed'].items():
        print(f"  0x{addr:x}: {instruction}")

    print("\nModified instructions:")
    for addr, (original, modified) in diff['modified'].items():
        print(f"  0x{addr:x}: Original: {original} | Modified: {modified}")


def main():
    """
    Main function to orchestrate the binary diffing process.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Input validation
    if not validate_file(args.file1):
        sys.exit(1)
    if not validate_file(args.file2):
        sys.exit(1)

    try:
        # Disassemble the binary files
        logging.info(f"Disassembling {args.file1}...")
        assembly1 = disassemble(args.file1, args.architecture)
        if assembly1 is None:
            sys.exit(1)

        logging.info(f"Disassembling {args.file2}...")
        assembly2 = disassemble(args.file2, args.architecture)
        if assembly2 is None:
            sys.exit(1)


        # Compare the assemblies
        logging.info("Comparing assemblies...")
        diff = diff_assemblies(assembly1, assembly2)

        # Output the diff
        if args.output:
            if not write_diff_to_file(diff, args.output):
                sys.exit(1)
        else:
            print_diff_to_console(diff)

        logging.info("Binary diff completed.")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

