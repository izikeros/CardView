#!/usr/bin/env python3
"""
Translation Build Script for CardView Plugin

This script helps manage the translation workflow for the CardView plugin.
It provides functions to extract strings, update translations, and compile
message catalogs.

Usage:
    python scripts/build_translations.py extract
    python scripts/build_translations.py update
    python scripts/build_translations.py compile
    python scripts/build_translations.py all
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

# Plugin configuration
DOMAIN = "cardview"
PROJECT_ROOT = Path(__file__).parent.parent
PO_DIR = PROJECT_ROOT / "po"
LOCALE_DIR = PROJECT_ROOT / "locale"
POTFILES = PO_DIR / "POTFILES.in"
POT_FILE = PO_DIR / f"{DOMAIN}.pot"


def run_command(cmd, check=True):
    """Run a shell command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def extract_strings():
    """Extract translatable strings to create/update POT file."""
    print("Extracting translatable strings...")

    if not POTFILES.exists():
        print(f"Error: {POTFILES} not found")
        sys.exit(1)

    cmd = [
        "xgettext",
        f"--files-from={POTFILES}",
        "--keyword=_",
        "--keyword=_plugin",
        "--language=Python",
        "--add-comments=TRANSLATORS:",
        "--sort-output",
        f"--package-name=CardView",
        "--msgid-bugs-address=your-email@domain.com",
        f"--output={POT_FILE}",
    ]

    # Change to project root for relative paths
    os.chdir(PROJECT_ROOT)
    run_command(cmd)
    print(f"POT file created: {POT_FILE}")


def update_po_files():
    """Update existing PO files with new strings from POT file."""
    print("Updating PO files...")

    if not POT_FILE.exists():
        print("POT file not found. Running extract first...")
        extract_strings()

    po_files = glob.glob(str(PO_DIR / "*.po"))

    if not po_files:
        print("No PO files found. Use 'make add-lang LANG=xx' to create new ones.")
        return

    for po_file in po_files:
        print(f"Updating {po_file}...")
        cmd = ["msgmerge", "--update", po_file, str(POT_FILE)]
        run_command(cmd)


def compile_mo_files():
    """Compile PO files to MO files."""
    print("Compiling MO files...")

    po_files = glob.glob(str(PO_DIR / "*.po"))

    if not po_files:
        print("No PO files found to compile.")
        return

    for po_file in po_files:
        po_path = Path(po_file)
        lang = po_path.stem

        # Create locale directory structure
        mo_dir = LOCALE_DIR / lang / "LC_MESSAGES"
        mo_dir.mkdir(parents=True, exist_ok=True)

        mo_file = mo_dir / f"{DOMAIN}.mo"

        print(f"Compiling {po_file} -> {mo_file}")
        cmd = ["msgfmt", po_file, "-o", str(mo_file)]
        run_command(cmd)


def validate_setup():
    """Validate that required tools are available."""
    tools = ["xgettext", "msgmerge", "msgfmt", "msginit"]
    missing = []

    for tool in tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(tool)

    if missing:
        print("Error: Missing required tools:")
        for tool in missing:
            print(f"  - {tool}")
        print("\nOn macOS: brew install gettext")
        print("On Ubuntu: sudo apt-get install gettext")
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    # Validate tools first
    validate_setup()

    if command == "extract":
        extract_strings()
    elif command == "update":
        update_po_files()
    elif command == "compile":
        compile_mo_files()
    elif command == "all":
        extract_strings()
        update_po_files()
        compile_mo_files()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
