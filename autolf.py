"""
Auto-LF script.
Change line-ending from each file (matched in WHITELIST).
From: https://gist.github.com/jonlabelle/dd8c3caa7808cbe4cfe0a47ee4881059
"""

import argparse
import os
import re
import sys

UNIX_NEWLINE = b"\n"
WINDOWS_NEWLINE = b"\r\n"
MAC_NEWLINE = b"\r"

WHITELIST = [r".*\.p(y|o)$", r".*\.html?$", r".*\.txt$", r".*\.sh$", r".*\.(j|t)sx?$"]
FOLDERS_BLACKLIST = [
    ".git",
]


def _is_binary_check(f):
    """Check if file is binary."""
    try:
        with open(f, "r", encoding="utf-8") as f:
            f.read()
            return False
    except UnicodeDecodeError:
        return True


def _walk_in_folder(r):
    """Walk in folder."""
    if os.path.isfile(r):
        return [r]

    fs = []
    for root, dirs, files in os.walk(r):
        for dirname in FOLDERS_BLACKLIST:
            if dirname in dirs:
                dirs.remove(dirname)

        for f in files:
            file_ok = False
            for e in WHITELIST:
                if re.match(e, f):
                    file_ok = True
                    break

            if file_ok:
                fs.append(os.path.join(root, f))
    return fs


def _normalize_line_endings(lines, line_ending="unix"):
    """Normalize line endings to unix, windows or mac.
    :param lines: The lines to normalize.
    :param line_ending: The line ending format.
    Acceptable values are 'unix' (default), 'windows' and 'mac'.
    :return: Line endings normalized.
    """
    lines = lines.replace(WINDOWS_NEWLINE, UNIX_NEWLINE).replace(MAC_NEWLINE, UNIX_NEWLINE)
    if line_ending == "windows":
        lines = lines.replace(UNIX_NEWLINE, WINDOWS_NEWLINE)
    elif line_ending == "mac":
        lines = lines.replace(UNIX_NEWLINE, MAC_NEWLINE)
    return lines


def _read_file_data(filepath):
    """Read file data.
    :param filepath: The file path.
    :return: The file contents.
    """
    data = open(filepath, "rb").read()
    return data


def _write_file_data(filepath, data):
    """Write file data.
    :param filepath: The file path.
    :param data: The data to write.
    """
    f = open(filepath, "wb")
    f.write(data)
    f.close()


def main():
    """Main."""
    parser = argparse.ArgumentParser(prog="autolf", description="Replace CRLF (windows) line endings with LF (unix)")
    parser.add_argument("-c", "--check", help="check", action="store_true", default=False)
    parser.add_argument("-q", "--quiet", help="quiet", action="store_true", default=False)
    parser.add_argument("path", nargs="?", help="path")

    args = parser.parse_args()
    if args.path:
        files_to_process = _walk_in_folder(args.path)
    else:
        files_to_process = _walk_in_folder(".")

    if len(files_to_process) <= 0:
        sys.stderr.write("No files matched the specified pattern.\n")
        sys.exit(2)

    if args.check is True:
        print("Checking...")
    else:
        print("Replacing...")

    # Track modifications
    changes_needed = False
    changes_count = 0
    processed_files = 0

    for file_to_process in files_to_process:
        if os.path.isdir(file_to_process):
            if not args.quiet:
                print("- '{0}' : is a directory (skip)".format(file_to_process))
            continue

        if os.path.isfile(file_to_process):
            data = _read_file_data(file_to_process)
            if _is_binary_check(file_to_process):
                if not args.quiet:
                    print("- '{0}' : is a binary file (skip)".format(file_to_process))
                continue

            processed_files += 1
            newdata = _normalize_line_endings(data, line_ending="unix")

            if newdata != data:
                changes_count += 1
                changes_needed = True

                if not args.quiet:
                    if args.check is True:
                        print("+ '{0}' : CRLF would be replaced with LF".format(file_to_process))
                    else:
                        print("+ '{0}' : replacing CRLF with LF".format(file_to_process))

                if args.check is False:
                    try:
                        # overwrite the current file with the modfified contents
                        _write_file_data(file_to_process, newdata)
                    except Exception as ex:
                        sys.stderr.write("error : {0}\n".format(str(ex)))
                        sys.exit(1)
        else:
            sys.stderr.write("- '{0}' : file not found\n".format(file_to_process))
            sys.exit(1)

    # End!
    if args.check:
        if changes_needed:
            print(f"{changes_count} files are in CRLF format. You need to fix.")
            sys.exit(1)
        else:
            print(f"{processed_files} files checked. All good!")
            sys.exit(0)
    else:
        print(f"{changes_count} files converted to LF. All good!")


if __name__ == "__main__":
    main()
