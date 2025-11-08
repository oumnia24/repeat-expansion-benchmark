#!/bin/bash
#SBATCH --job-name=paternal_mm2_index
#SBATCH --output=logs/paternal_minimap2_index_%j.out
#SBATCH --error=logs/paternal_minimap2_index_%j.err
#SBATCH --time=6:00:00
#SBATCH --mem=384G
#SBATCH --cpus-per-task=64
#SBATCH --partition=bigmem

# Load minimap2 module
module load biology minimap2

echo "Building minimap2 index for paternal assembly..."
minimap2 -t 64 -d ../data/hg002v1.1_paternal.mmi ../data/hg002v1.1_paternal.fasta.gz

echo "Paternal index building complete!"
ls -lh ../data/hg002v1.1_paternal.mmi
