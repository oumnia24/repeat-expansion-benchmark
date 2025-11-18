#!/usr/bin/env python3
"""
Analyze flank alignment quality from SAM files.
Generates MAPQ distribution plots and alignment statistics.
"""

import matplotlib.pyplot as plt
from collections import Counter
import argparse
import sys

def parse_mapq_scores(sam_file):
    """
    Extract MAPQ scores from SAM file using simple text parsing.

    Returns:
        list: MAPQ scores for all alignments
    """
    mapq_scores = []

    with open(sam_file, 'r') as sam:
        for line in sam:
            # Skip header lines
            if line.startswith('@'):
                continue

            # Parse SAM fields (tab-separated)
            fields = line.strip().split('\t')
            if len(fields) < 11:
                continue

            # Column 5 is MAPQ (0-indexed: column 4)
            try:
                mapq = int(fields[4])
                mapq_scores.append(mapq)
            except (ValueError, IndexError):
                continue

    return mapq_scores

def plot_mapq_distribution(maternal_mapq, paternal_mapq, output_prefix):
    """
    Create MAPQ distribution plots.

    Args:
        maternal_mapq: List of maternal MAPQ scores
        paternal_mapq: List of paternal MAPQ scores
        output_prefix: Prefix for output files
    """
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Maternal MAPQ distribution
    maternal_counts = Counter(maternal_mapq)
    maternal_sorted = sorted(maternal_counts.items())
    maternal_x = [x[0] for x in maternal_sorted]
    maternal_y = [x[1] for x in maternal_sorted]

    ax1.bar(maternal_x, maternal_y, color='#e74c3c', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('MAPQ Score', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_title('Maternal Flank Alignments - MAPQ Distribution', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_xlim(-5, 65)

    # Add text box with stats
    total_mat = len(maternal_mapq)
    mapq60_mat = maternal_counts.get(60, 0)
    mapq0_mat = maternal_counts.get(0, 0)
    ax1.text(0.98, 0.97,
             f'Total: {total_mat:,}\nMAPQ=60: {mapq60_mat:,} ({100*mapq60_mat/total_mat:.1f}%)\nMAPQ=0: {mapq0_mat:,} ({100*mapq0_mat/total_mat:.1f}%)',
             transform=ax1.transAxes,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
             fontsize=10)

    # Paternal MAPQ distribution
    paternal_counts = Counter(paternal_mapq)
    paternal_sorted = sorted(paternal_counts.items())
    paternal_x = [x[0] for x in paternal_sorted]
    paternal_y = [x[1] for x in paternal_sorted]

    ax2.bar(paternal_x, paternal_y, color='#3498db', alpha=0.7, edgecolor='black')
    ax2.set_xlabel('MAPQ Score', fontsize=12)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.set_title('Paternal Flank Alignments - MAPQ Distribution', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_xlim(-5, 65)

    # Add text box with stats
    total_pat = len(paternal_mapq)
    mapq60_pat = paternal_counts.get(60, 0)
    mapq0_pat = paternal_counts.get(0, 0)
    ax2.text(0.98, 0.97,
             f'Total: {total_pat:,}\nMAPQ=60: {mapq60_pat:,} ({100*mapq60_pat/total_pat:.1f}%)\nMAPQ=0: {mapq0_pat:,} ({100*mapq0_pat/total_pat:.1f}%)',
             transform=ax2.transAxes,
             verticalalignment='top',
             horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
             fontsize=10)

    plt.tight_layout()
    plt.savefig(f'{output_prefix}_mapq_distribution.png', dpi=300, bbox_inches='tight')
    print(f"Saved plot: {output_prefix}_mapq_distribution.png")
    plt.close()

def print_summary_stats(maternal_mapq, paternal_mapq):
    """
    Print summary statistics to console.
    """
    print("\n" + "="*70)
    print("ALIGNMENT QUALITY SUMMARY")
    print("="*70)

    # Maternal stats
    maternal_counts = Counter(maternal_mapq)
    total_mat = len(maternal_mapq)
    mapq60_mat = maternal_counts.get(60, 0)
    mapq0_mat = maternal_counts.get(0, 0)
    mapq_high_mat = sum(count for mapq, count in maternal_counts.items() if mapq >= 20)

    print("\nMATERNAL ALIGNMENTS:")
    print(f"  Total alignments:        {total_mat:,}")
    print(f"  MAPQ = 60 (unique):      {mapq60_mat:,} ({100*mapq60_mat/total_mat:.1f}%)")
    print(f"  MAPQ >= 20 (high qual):  {mapq_high_mat:,} ({100*mapq_high_mat/total_mat:.1f}%)")
    print(f"  MAPQ = 0 (ambiguous):    {mapq0_mat:,} ({100*mapq0_mat/total_mat:.1f}%)")

    # Paternal stats
    paternal_counts = Counter(paternal_mapq)
    total_pat = len(paternal_mapq)
    mapq60_pat = paternal_counts.get(60, 0)
    mapq0_pat = paternal_counts.get(0, 0)
    mapq_high_pat = sum(count for mapq, count in paternal_counts.items() if mapq >= 20)

    print("\nPATERNAL ALIGNMENTS:")
    print(f"  Total alignments:        {total_pat:,}")
    print(f"  MAPQ = 60 (unique):      {mapq60_pat:,} ({100*mapq60_pat/total_pat:.1f}%)")
    print(f"  MAPQ >= 20 (high qual):  {mapq_high_pat:,} ({100*mapq_high_pat/total_pat:.1f}%)")
    print(f"  MAPQ = 0 (ambiguous):    {mapq0_pat:,} ({100*mapq0_pat/total_pat:.1f}%)")

    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze flank alignment quality from SAM files"
    )
    parser.add_argument("maternal_sam", help="Maternal SAM file")
    parser.add_argument("paternal_sam", help="Paternal SAM file")
    parser.add_argument("--output-prefix", default="../data/flank_alignment_analysis",
                       help="Output prefix for plots (default: ../data/flank_alignment_analysis)")

    args = parser.parse_args()

    print("Parsing maternal alignments...")
    maternal_mapq = parse_mapq_scores(args.maternal_sam)
    print(f"  Found {len(maternal_mapq):,} alignments")

    print("Parsing paternal alignments...")
    paternal_mapq = parse_mapq_scores(args.paternal_sam)
    print(f"  Found {len(paternal_mapq):,} alignments")

    print("\nGenerating plots...")
    plot_mapq_distribution(maternal_mapq, paternal_mapq, args.output_prefix)

    print_summary_stats(maternal_mapq, paternal_mapq)
