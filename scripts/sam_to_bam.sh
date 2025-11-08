#!/bin/bash
#SBATCH --job-name=sam_to_bam
#SBATCH --mem=300G
#SBATCH --partition=bigmem
#SBATCH --cpus-per-task=12
#SBATCH --time=00:30:00
#SBATCH --output=logs/sam_to_bam_%j.out
#SBATCH --error=logs/sam_to_bam_%j.err

# Load samtools module
module load biology samtools

# Change to data directory
cd ../data

# Convert SAM to BAM
samtools view -@ 12 -Sb SRR26402938.sam > SRR26402938.bam