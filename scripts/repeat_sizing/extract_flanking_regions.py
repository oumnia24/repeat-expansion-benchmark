#!/usr/bin/env python3
import pysam
import sys

def extract_flanking_sequences(bed_file, fasta_file, output_file, flank_size=250):
    """
    Extract flanking sequences from repeat regions defined in BED file
    """
    # Open the reference genome
    fasta = pysam.FastaFile(fasta_file)
    
    # Read the BED file
    with open(bed_file, 'r') as bed, open(output_file, 'w') as out:
        for line in bed:
            if line.startswith('#'):
                continue
                
            fields = line.strip().split('\t')
            chrom = fields[0]
            start = int(fields[1])
            end = int(fields[2])
            
            # Extract the repeat identifier from the ID field
            # Format: ID=chr1_16682_16774_TGGTGGGGG;MOTIFS=...
            id_field = fields[3].split(';')[0]  # Get "ID=chr1_16682_16774_TGGTGGGGG"
            repeat_identifier = id_field.replace('ID=', '')  # Remove "ID=" prefix
            
            # Skip if chromosome not in reference
            if chrom not in fasta.references:
                print(f"Warning: {chrom} not found in reference", file=sys.stderr)
                continue
            
            # Get chromosome length
            chrom_len = fasta.get_reference_length(chrom)
            
            # Calculate flank positions (ensure they don't go beyond chromosome boundaries)
            left_flank_start = max(0, start - flank_size)
            left_flank_end = start
            
            right_flank_start = end
            right_flank_end = min(chrom_len, end + flank_size)
            
            # Extract sequences
            left_flank_seq = fasta.fetch(chrom, left_flank_start, left_flank_end)
            right_flank_seq = fasta.fetch(chrom, right_flank_start, right_flank_end)
            
            # Write output with _LF and _RF naming convention
            out.write(f">{repeat_identifier}_LF\n")
            out.write(f"{left_flank_seq}\n")
            
            out.write(f">{repeat_identifier}_RF\n")
            out.write(f"{right_flank_seq}\n")
    
    fasta.close()
    print(f"Flanking sequences written to {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract flanking sequences from repeat regions")
    parser.add_argument("bed_file", help="BED file with repeat regions")
    parser.add_argument("fasta_file", help="Reference genome FASTA file")
    parser.add_argument("output_file", help="Output FASTA file with flanking sequences")
    parser.add_argument("--flank-size", type=int, default=250, help="Size of flanking region (default: 250)")
    
    args = parser.parse_args()
    
    extract_flanking_sequences(args.bed_file, args.fasta_file, args.output_file, args.flank_size)