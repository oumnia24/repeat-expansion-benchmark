#!/usr/bin/env python3
"""
Split haplotype-resolved HG002 assembly into maternal and paternal FASTA files.
"""

import gzip
import sys

def split_haplotypes(input_file, maternal_output, paternal_output):
    """
    Split a haplotype-resolved assembly into maternal and paternal files.

    Args:
        input_file: Path to input gzipped FASTA file
        maternal_output: Path to maternal output FASTA file
        paternal_output: Path to paternal output FASTA file
    """
    maternal_count = 0
    paternal_count = 0

    with gzip.open(input_file, 'rt') as infile, \
         gzip.open(maternal_output, 'wt') as mat_out, \
         gzip.open(paternal_output, 'wt') as pat_out:

        current_output = None

        for line in infile:
            if line.startswith('>'):
                # Determine which file to write to
                if '_MATERNAL' in line or 'chrM' in line:
                    current_output = mat_out
                    maternal_count += 1
                elif '_PATERNAL' in line:
                    current_output = pat_out
                    paternal_count += 1
                else:
                    print(f"Warning: Unrecognized chromosome: {line.strip()}", file=sys.stderr)
                    current_output = None

            # Write all lines (headers and sequences)
            if current_output:
                current_output.write(line)

    print(f"Split complete!")
    print(f"  Maternal chromosomes: {maternal_count}")
    print(f"  Paternal chromosomes: {paternal_count}")

if __name__ == "__main__":
    # Paths relative to project root (script will be run from scripts/ dir)
    input_file = "../data/hg002v1.1.fasta.gz"
    maternal_output = "../data/hg002v1.1_maternal.fasta.gz"
    paternal_output = "../data/hg002v1.1_paternal.fasta.gz"

    print(f"Splitting haplotypes from: {input_file}")
    print(f"  -> Maternal output: {maternal_output}")
    print(f"  -> Paternal output: {paternal_output}")
    print()

    split_haplotypes(input_file, maternal_output, paternal_output)
