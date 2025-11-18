#!/usr/bin/env python3
"""
Filter high-quality SAM file (MAPQ=60) to keep only repeat regions where:
1. Both left (LF) and right (RF) flanks are present
2. Both flanks map to the same chromosome
3. The mapped chromosome matches the expected chromosome from the repeat ID

Input: flanks_maternal_high_quality.sam or flanks_paternal_high_quality.sam
"""

import sys
import argparse
from collections import defaultdict

def parse_sam_and_filter(input_sam, output_sam):
    """
    Filter SAM file to keep only properly paired flanks.

    Args:
        input_sam: Input high-quality SAM file (MAPQ=60)
        output_sam: Output filtered SAM file
    """
    # Store header lines
    headers = []

    # Store alignments grouped by repeat ID
    # Key: repeat_id (e.g., "chr1_784053_784142_TA")
    # Value: {'LF': {'line': ..., 'mapped_chr': ...}, 'RF': {...}}
    alignments = defaultdict(dict)

    # Parse SAM file
    with open(input_sam, 'r') as f:
        for line in f:
            # Save header lines
            if line.startswith('@'):
                headers.append(line)
                continue

            fields = line.strip().split('\t')
            if len(fields) < 11:
                continue

            flank_name = fields[0]  # e.g., "chr1_286104_286208_TG_LF"
            mapped_chr = fields[2]  # e.g., "chr20_MATERNAL"

            # Extract flank type and repeat ID
            flank_type = flank_name[-2:]  # "LF" or "RF"
            repeat_id = flank_name[:-3]   # Remove "_LF" or "_RF"

            if flank_type not in ['LF', 'RF']:
                continue

            # Store the full SAM line and mapped chromosome
            alignments[repeat_id][flank_type] = {
                'line': line,
                'mapped_chr': mapped_chr
            }

    # Filter: keep only repeats with both LF and RF that map to correct chromosome
    kept_count = 0
    discarded_no_pair = 0
    discarded_diff_chr = 0
    discarded_wrong_chr = 0

    filtered_lines = []

    for repeat_id, flanks in alignments.items():
        # Check if both LF and RF exist
        if 'LF' not in flanks or 'RF' not in flanks:
            discarded_no_pair += 1
            continue

        lf_mapped_chr = flanks['LF']['mapped_chr']
        rf_mapped_chr = flanks['RF']['mapped_chr']

        # Check if both map to the same chromosome
        if lf_mapped_chr != rf_mapped_chr:
            discarded_diff_chr += 1
            continue

        # Extract reference chromosome from repeat ID
        # Format: chr1_784053_784142_TA
        # Reference chromosome is "chr1"
        ref_chr = repeat_id.split('_')[0]

        # Check if they map to the correct chromosome (chr1_MATERNAL or chr1_PATERNAL)
        if not lf_mapped_chr.startswith(f"{ref_chr}_"):
            discarded_wrong_chr += 1
            continue

        # Keep both flanks
        filtered_lines.append(flanks['LF']['line'])
        filtered_lines.append(flanks['RF']['line'])
        kept_count += 1

    # Write output SAM file
    with open(output_sam, 'w') as out:
        # Write headers
        for header in headers:
            out.write(header)

        # Write filtered alignments
        for line in filtered_lines:
            out.write(line)

    # Print statistics
    print(f"\n{'='*70}")
    print(f"FILTERING RESULTS")
    print(f"{'='*70}")
    print(f"Total repeat regions analyzed:     {len(alignments):,}")
    print(f"Kept (both flanks, correct chr):   {kept_count:,} ({100*kept_count/len(alignments):.1f}%)")
    print(f"Discarded (missing LF or RF):      {discarded_no_pair:,}")
    print(f"Discarded (LF/RF diff chr):        {discarded_diff_chr:,}")
    print(f"Discarded (wrong chromosome):      {discarded_wrong_chr:,}")
    print(f"{'='*70}\n")

    print(f"Output written to: {output_sam}")
    print(f"  Total alignment lines: {len(filtered_lines):,} (= {kept_count:,} × 2 flanks)\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Filter SAM file to keep only properly paired flanks"
    )
    parser.add_argument("input_sam", help="Input high-quality SAM file")

    args = parser.parse_args()

    # Auto-generate output filename
    output_sam = args.input_sam.replace('_high_quality.sam', '_filtered.sam')
    if output_sam == args.input_sam:
        # Fallback if pattern not found
        output_sam = args.input_sam.replace('.sam', '_filtered.sam')

    parse_sam_and_filter(args.input_sam, output_sam)
