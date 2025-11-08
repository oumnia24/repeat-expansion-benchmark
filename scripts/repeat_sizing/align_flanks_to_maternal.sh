#!/bin/bash
#SBATCH --job-name=align_maternal
#SBATCH --output=logs/align_maternal_%j.out
#SBATCH --error=logs/align_maternal_%j.err
#SBATCH --time=4:00:00
#SBATCH --mem=384G
#SBATCH --cpus-per-task=64
#SBATCH --partition=bigmem

# Load minimap2 module
module load biology minimap2

echo "Aligning flanking regions to maternal chromosomes..."
minimap2 -t 64 -ax asm5 \
    ../data/hg002v1.1_maternal.mmi \
    ../data/hg002_repeat_region_flanks.fa \
    > ../data/flanks_maternal.sam

echo "Alignment complete!"
ls -lh ../data/flanks_maternal.sam
