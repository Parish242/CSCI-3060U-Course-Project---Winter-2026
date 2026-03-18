"""
backend/merge_transactions.py

Merges one or more Front End transaction files into a single merged transaction
file ready for the Back End to process.

The Front End writes one transaction file per session named with a timestamp:
    MM-DD-YYYY HH-MM-SS.txt
    e.g.  03-12-2026 14-05-33.txt

This script scans a source directory for all files matching that pattern,
sorts them chronologically by filename, strips every intermediate end-of-session
record (code 00), and writes a single merged file ending with exactly one
end-of-session record.

Usage:
    python merge_transactions.py [source_dir] [output_file]

Arguments (both optional):
    source_dir   - directory to scan for Front End transaction files.
                   Defaults to the Frontend/ directory relative to the repo root.
    output_file  - path to write the merged output.
                   Defaults to merged_transactions.txt in the repo root.
"""

import os
import re
import sys


# Pattern that matches Front End transaction filenames: MM-DD-YYYY HH-MM-SS.txt
TRANSACTION_FILE_PATTERN = re.compile(
    r"^\d{2}-\d{2}-\d{4} \d{2}-\d{2}-\d{2}\.txt$"
)

# The end-of-session record written by the Front End (code 00).
END_OF_SESSION_PREFIX = "00 "


def find_transaction_files(source_dir: str) -> list[str]:
    """
    Return a sorted list of Front End transaction file paths found in source_dir.

    Files are sorted chronologically by filename (which encodes the timestamp).

    Args:
        source_dir: Directory to scan.

    Returns:
        List of absolute file paths, sorted oldest-first.
    """
    if not os.path.isdir(source_dir):
        print(f"ERROR: Source directory not found: {source_dir}")
        return []

    matches = [
        os.path.join(source_dir, f)
        for f in sorted(os.listdir(source_dir))
        if TRANSACTION_FILE_PATTERN.match(f)
    ]
    return matches


def merge(source_dir: str, output_file: str) -> bool:
    """
    Merge all Front End transaction files from source_dir into output_file.

    For each input file, every line except end-of-session (code 00) records is
    written to the output. A single end-of-session record is appended at the end.

    Args:
        source_dir:  Directory containing Front End transaction files.
        output_file: Path to write the merged transaction file.

    Returns:
        True if at least one file was merged, False otherwise.
    """
    files = find_transaction_files(source_dir)

    if not files:
        print(f"No transaction files found in: {source_dir}")
        return False

    print(f"Merging {len(files)} transaction file(s):")
    for f in files:
        print(f"  {os.path.basename(f)}")

    with open(output_file, "w") as out:
        for path in files:
            with open(path, "r") as fh:
                for line in fh:
                    # Skip end-of-session records from individual files;
                    # a single one will be written after all files are merged.
                    if line.startswith(END_OF_SESSION_PREFIX):
                        continue
                    out.write(line)

        # Write the single end-of-session record that terminates the merged file.
        out.write("00 END_OF_FILE          00000 00000000 00\n")

    print(f"Merged output written to: {output_file}")
    return True


def main() -> None:
    """Parse arguments and run the merge."""
    args     = sys.argv[1:]
    base_dir = os.path.join(os.path.dirname(__file__), "..")

    source_dir  = args[0] if len(args) >= 1 else base_dir
    output_file = args[1] if len(args) >= 2 else os.path.join(base_dir, "merged_transactions.txt")

    merge(source_dir, output_file)


if __name__ == "__main__":
    main()
