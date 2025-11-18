#!/usr/bin/env python3
"""
Filter catalog repeat regions based on regions present in flanks SAM file.

This script reads a SAM file containing flank alignments and a catalog BED file
of repeat regions, then outputs a filtered catalog containing only regions that
have corresponding flanks in the SAM file.
"""

import argparse
import sys
from pathlib import Path
from typing import Set, Tuple


def parse_sam_regions(sam_file: str) -> Set[Tuple[str, int, int]]:
    """
    Extract unique genomic regions from SAM file read names.

    Read names are expected to be in format:
    chr{chrom}_{start}_{end}_{repeat_unit}_{LF/RF}

    Args:
        sam_file: Path to SAM file

    Returns:
        Set of tuples (chromosome, start, end) for each unique region
    """
    regions = set()
    line_count = 0

    print(f"Parsing SAM file: {sam_file}", file=sys.stderr)

    with open(sam_file, 'r') as f:
        for line in f:
            # Skip header lines
            if line.startswith('@'):
                continue

            line_count += 1
            if line_count % 100000 == 0:
                print(f"  Processed {line_count} alignments, found {len(regions)} unique regions...", file=sys.stderr)

            # Extract read name (first column)
            fields = line.strip().split('\t')
            if len(fields) == 0:
                continue

            read_name = fields[0]

            # Parse read name: chr{chrom}_{start}_{end}_{repeat_unit}_{LF/RF}
            # Split by underscore and extract chr, start, end
            parts = read_name.split('_')

            if len(parts) < 3:
                print(f"Warning: Could not parse read name: {read_name}", file=sys.stderr)
                continue

            try:
                chrom = parts[0]  # e.g., chr1
                start = int(parts[1])
                end = int(parts[2])
                regions.add((chrom, start, end))
            except (ValueError, IndexError) as e:
                print(f"Warning: Could not parse coordinates from read name: {read_name}", file=sys.stderr)
                continue

    print(f"  Total alignments processed: {line_count}", file=sys.stderr)
    print(f"  Unique regions found: {len(regions)}", file=sys.stderr)

    return regions


def filter_catalog(catalog_file: str, regions: Set[Tuple[str, int, int]], output_file: str):
    """
    Filter catalog BED file to keep only regions present in the flanks SAM file.

    Args:
        catalog_file: Path to input catalog BED file
        regions: Set of (chromosome, start, end) tuples from SAM file
        output_file: Path to output filtered catalog file
    """
    matched_count = 0
    total_count = 0

    print(f"Filtering catalog file: {catalog_file}", file=sys.stderr)

    with open(catalog_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Skip empty lines
            if not line.strip():
                continue

            total_count += 1

            # Parse BED file (tab-separated)
            fields = line.strip().split('\t')

            if len(fields) < 3:
                print(f"Warning: Invalid BED line (< 3 fields): {line.strip()}", file=sys.stderr)
                continue

            try:
                chrom = fields[0]
                start = int(fields[1])
                end = int(fields[2])

                # Check if this region is in our set (O(1) hash lookup)
                if (chrom, start, end) in regions:
                    outfile.write(line)
                    matched_count += 1

            except ValueError as e:
                print(f"Warning: Could not parse coordinates from catalog line: {line.strip()}", file=sys.stderr)
                continue

    print(f"  Total catalog regions: {total_count}", file=sys.stderr)
    print(f"  Matched regions: {matched_count}", file=sys.stderr)
    print(f"  Filtered catalog written to: {output_file}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='Filter catalog repeat regions based on regions present in flanks SAM file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  ./repeat_sizing/filter_catalog_by_flanks.py \\
    --sam ../data/flanks_maternal_filtered.sam \\
    --catalog ../catalogs/adotto_repeats.hg38.bed \\
    --output ../catalogs/adotto_repeats_filtered.bed
        """
    )
    parser.add_argument(
        '--sam',
        required=True,
        help='Input SAM file with flank alignments'
    )
    parser.add_argument(
        '--catalog',
        required=True,
        help='Input catalog BED file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output filtered catalog BED file'
    )

    args = parser.parse_args()

    # Check input files exist
    if not Path(args.sam).exists():
        print(f"Error: SAM file not found: {args.sam}", file=sys.stderr)
        sys.exit(1)

    if not Path(args.catalog).exists():
        print(f"Error: Catalog file not found: {args.catalog}", file=sys.stderr)
        sys.exit(1)

    # Parse regions from SAM file
    regions = parse_sam_regions(args.sam)

    if len(regions) == 0:
        print("Error: No regions found in SAM file", file=sys.stderr)
        sys.exit(1)

    # Filter catalog file
    filter_catalog(args.catalog, regions, args.output)

    print("Done!", file=sys.stderr)


if __name__ == '__main__':
    main()
