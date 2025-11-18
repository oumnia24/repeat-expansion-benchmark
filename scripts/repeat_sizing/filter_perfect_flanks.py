#!/usr/bin/env python3
"""
Filter SAM file to keep only regions where both LF and RF have perfect 250M CIGAR.

This script reads a SAM file with flank alignments and outputs only the reads
where both the left flank (LF) and right flank (RF) of the same repeat region
have a CIGAR string of exactly "250M" (perfect alignment).

Assumes LF and RF pairs are adjacent in the input file.
"""

import argparse
import sys
from pathlib import Path


def get_region_key(read_name: str) -> str:
    """Extract region key from read name (everything except LF/RF)."""
    parts = read_name.split('_')
    return '_'.join(parts[:-1])


def get_flank_type(read_name: str) -> str:
    """Extract flank type (LF or RF) from read name."""
    return read_name.split('_')[-1]


def get_cigar(line: str) -> str:
    """Extract CIGAR string from SAM line."""
    return line.split('\t')[5]


def filter_perfect_flanks(input_file: str, output_file: str):
    """
    Filter SAM file to keep only perfect flank pairs (both 250M).

    Args:
        input_file: Path to input SAM file
        output_file: Path to output SAM file
    """
    perfect_pairs = 0
    skipped_pairs = 0
    total_reads_written = 0

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        previous_line = None
        previous_read_name = None

        for line in infile:
            # Write header lines as-is
            if line.startswith('@'):
                outfile.write(line)
                continue

            fields = line.strip().split('\t')
            if len(fields) < 6:
                continue

            read_name = fields[0]
            flank_type = get_flank_type(read_name)

            # If this is a left flank, store it and continue
            if flank_type == 'LF':
                previous_line = line
                previous_read_name = read_name
                continue

            # If this is a right flank, check if it pairs with previous LF
            if flank_type == 'RF' and previous_line is not None:
                # Check if they're from the same region
                current_region = get_region_key(read_name)
                previous_region = get_region_key(previous_read_name)

                if current_region == previous_region:
                    # Check if both have 250M CIGAR
                    lf_cigar = get_cigar(previous_line)
                    rf_cigar = get_cigar(line)

                    if lf_cigar == '250M' and rf_cigar == '250M':
                        # Write both lines
                        outfile.write(previous_line)
                        outfile.write(line)
                        perfect_pairs += 1
                        total_reads_written += 2
                    else:
                        skipped_pairs += 1

                # Reset for next pair
                previous_line = None
                previous_read_name = None

    print(f"Perfect pairs (both 250M): {perfect_pairs}", file=sys.stderr)
    print(f"Skipped pairs: {skipped_pairs}", file=sys.stderr)
    print(f"Total reads written: {total_reads_written}", file=sys.stderr)
    print(f"Output written to: {output_file}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Filter SAM file to keep only regions where both LF and RF have 250M CIGAR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  ./repeat_sizing/filter_perfect_flanks.py \\
    --input ../data/flanks_maternal_filtered.sam \\
    --output ../data/flanks_maternal_perfect.sam
        """
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input SAM file with flank alignments'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output SAM file with only perfect pairs'
    )

    args = parser.parse_args()

    # Check input file exists
    if not Path(args.input).exists():
        print(f"Error: Input SAM file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Filter for perfect pairs
    filter_perfect_flanks(args.input, args.output)

    print("Done!", file=sys.stderr)


if __name__ == '__main__':
    main()
