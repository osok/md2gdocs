#!/usr/bin/env python3
"""Quick test to see what table parsing is producing."""

import re

# Read the table from example.md
with open('example.md', 'r') as f:
    content = f.read()

# Find table with regex - OLD BROKEN PATTERN
# table_pattern = r'(\|.+\|\n\|[\s\-:|]+\|(?:\n\|.+\|)*)'

# NEW FIXED PATTERN - matches multiple lines with pipes
table_pattern = r'(\|.+\|(?:\n\|.+\|)+)'
matches = re.findall(table_pattern, content, re.MULTILINE)

print(f"Found {len(matches)} tables\n")

for i, table_text in enumerate(matches):
    print(f"=== TABLE {i} ===")
    print(table_text)
    print()

    # Parse it
    lines = [line.strip() for line in table_text.strip().split('\n') if line.strip()]
    print(f"Total lines: {len(lines)}")

    # Parse header
    header_cells = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
    print(f"Header cells ({len(header_cells)}): {header_cells}")

    # Parse separator
    print(f"Separator: {lines[1]}")

    # Parse data rows
    print(f"\nData rows ({len(lines[2:])} rows):")
    for j, line in enumerate(lines[2:]):
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        print(f"  Row {j}: {len(cells)} cells - {cells[:2]}...")  # Show first 2 cells
