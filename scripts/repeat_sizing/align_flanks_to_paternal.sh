#!/bin/bash
#SBATCH --job-name=align_paternal
#SBATCH --output=logs/align_paternal_%j.out
#SBATCH --error=logs/align_paternal_%j.err
#SBATCH --time=4:00:00
#SBATCH --mem=384G
#SBATCH --cpus-per-task=64
#SBATCH --partition=bigmem

# Load minimap2 module
module load biology minimap2

echo "Aligning flanking regions to paternal chromosomes..."
minimap2 -t 64 -ax asm5 \
    ../data/hg002v1.1_paternal.mmi \
    ../data/hg002_repeat_region_flanks.fa \
    > ../data/flanks_paternal.sam

echo "Alignment complete!"
ls -lh ../data/flanks_paternal.sam
