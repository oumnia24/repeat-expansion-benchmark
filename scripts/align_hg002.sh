#!/bin/bash
#SBATCH --job-name=align_hg002
#SBATCH --mem=400G
#SBATCH --partition=bigmem
#SBATCH --cpus-per-task=12
#SBATCH --time=12:00:00
#SBATCH --output=logs/align_hg002_%j.out
#SBATCH --error=logs/align_hg002_%j.err

# Load minimap2 module
module load biology minimap2

# Change to data directory
cd ../data

# Align HG002 reads to hg38 reference
minimap2 -ax map-pb -t 12 hg38.fa SRR26402938.fastq > SRR26402938.sam