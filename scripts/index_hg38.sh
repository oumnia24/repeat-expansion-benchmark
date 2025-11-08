#!/bin/bash
#SBATCH --job-name=minimap2_index
#SBATCH --mem=32G
#SBATCH --partition=normal
#SBATCH --cpus-per-task=4
#SBATCH --time=00:10:00
#SBATCH --output=logs/minimap2_index_%j.out
#SBATCH --error=logs/minimap2_index_%j.err

# Load minimap2 module if needed
module load biology minimap2

# Create minimap2 index
minimap2 -d ../data/hg38.mmi ../data/hg38.fa