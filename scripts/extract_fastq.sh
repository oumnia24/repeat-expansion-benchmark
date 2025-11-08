#!/bin/bash
#SBATCH --job-name=fastq_dump
#SBATCH --mem=16G
#SBATCH --partition=normal
#SBATCH --cpus-per-task=2
#SBATCH --time=01:00:00
#SBATCH --output=logs/fastq_dump_%j.out
#SBATCH --error=logs/fastq_dump_%j.err

# Load SRA toolkit module
module load biology sratoolkit

# Change to data directory
cd ../data

# Extract FASTQ files from SRA
fastq-dump --split-files SRR26402938