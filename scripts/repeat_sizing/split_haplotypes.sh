#!/bin/bash
#SBATCH --job-name=split_haplotypes
#SBATCH --output=logs/split_haplotypes_%j.out
#SBATCH --error=logs/split_haplotypes_%j.err
#SBATCH --time=2:00:00
#SBATCH --mem=400G
#SBATCH --cpus-per-task=1
#SBATCH --partition=bigmem

# Run the Python script
python split_haplotypes.py
