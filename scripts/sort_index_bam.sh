#!/bin/bash
#SBATCH --job-name=sort_index_bam
#SBATCH --mem=300G
#SBATCH --partition=bigmem
#SBATCH --cpus-per-task=12
#SBATCH --time=02:00:00
#SBATCH --output=logs/sort_index_bam_%j.out
#SBATCH --error=logs/sort_index_bam_%j.err

# Load samtools module
module load biology samtools

# Change to data directory
cd ../data

# Sort BAM file
samtools sort -@ 12 SRR26402938.bam -o SRR26402938.sorted.bam

# Index sorted BAM file
samtools index -@ 12 SRR26402938.sorted.bam