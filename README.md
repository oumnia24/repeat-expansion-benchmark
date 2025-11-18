# Repeat Expansion Caller Benchmark Pipeline

This repository contains scripts for benchmarking repeat expansion callers on HG002 genome data using Stanford's Sherlock HPC cluster.

## Directory Structure

```
.
├── scripts/          # SLURM job scripts
│   └── logs/         # Job output logs and tracking
├── data/             # Input data (not tracked by git)
├── results/          # Analysis outputs
├── callers/          # Repeat expansion caller software
└── docs/             # Project documentation
```

## Pipeline Overview

The pipeline processes HG002 sequencing data through the following steps:

1. **Index Reference Genome** (`index_hg38.sh`)
   - Creates minimap2 index of hg38 reference genome
   - Input: `data/hg38.fa`
   - Output: `data/hg38.mmi` (~7GB)

2. **Extract FASTQ** (`extract_fastq.sh`)
   - Converts SRA format to FASTQ
   - Input: Downloaded SRA file
   - Output: FASTQ file(s)

3. **Align Reads** (`align_hg002.sh`)
   - Aligns HG002 reads to hg38 reference
   - Uses minimap2 with PacBio settings
   - Output: SAM file

4. **Convert to BAM** (`sam_to_bam.sh`)
   - Converts SAM to compressed BAM format
   - ~4-8x size reduction

5. **Sort and Index** (`sort_index_bam.sh`)
   - Sorts BAM by genomic position
   - Creates index for fast access

## Usage

### Running Scripts

All scripts must be run from the `scripts/` directory:

```bash
cd /scratch/users/oumnia/repeat-expansion-benchmark/scripts
sbatch script_name.sh
```

### Job Tracking

Use the `log_job.sh` wrapper to track job submissions:

```bash
./log_job.sh extract_fastq.sh
```

This creates entries in `logs/job_history.csv`:
- job_id: SLURM job identifier
- script: Script that was run
- date: Submission timestamp
- status: Job status (pending/completed)

### Monitoring Jobs

```bash
squeue -u $USER          # View your running jobs
sacct -j <job_id>        # View job details
seff <job_id>            # View job efficiency report
```

## Log Structure

All job outputs are stored in `scripts/logs/`:

- `<job_name>_<job_id>.out`: Standard output
- `<job_name>_<job_id>.err`: Error messages
- `job_history.csv`: Job submission tracking

Example log filename: `minimap2_index_9169173.out`

## Resource Requirements

| Script | Memory | CPUs | Partition | Runtime |
|--------|--------|------|-----------|---------|
| index_hg38.sh | 32GB | 4 | normal | ~2 min |
| extract_fastq.sh | 16GB | 2 | normal | ~1 hour |
| align_hg002.sh | 400GB | 12 | bigmem | ~2 hours |
| sam_to_bam.sh | 300GB | 12 | normal | ~6 min |
| sort_index_bam.sh | 300GB | 12 | normal | ~1.5 hours |

## Prerequisites

- Access to Stanford Sherlock cluster
- Required modules: `biology`, `minimap2`, `samtools`, `sratoolkit`
- Input data: hg38 reference genome, HG002 sequencing data

## Haplotype-Specific Repeat Sizing Pipeline

A separate analysis pipeline for measuring repeat sizes in maternal and paternal haplotypes using a haplotype-resolved HG002 assembly.

### Overview

This pipeline:
1. Extracts flanking regions around repeat loci from the reference genome
2. Splits a phased HG002 assembly into maternal and paternal chromosomes
3. Aligns flanking regions to both haplotypes
4. Calculates repeat sizes by measuring distances between aligned flanks

### Scripts Location

All repeat sizing scripts are in `scripts/repeat_sizing/`:

```
scripts/repeat_sizing/
├── extract_flanking_regions.py           # Extract flanks from reference
├── split_haplotypes.py                   # Split assembly by haplotype
├── split_haplotypes.sh                   # SLURM job for splitting
├── build_maternal_minimap2_index.sh      # Index maternal assembly
├── build_paternal_minimap2_index.sh      # Index paternal assembly
├── align_flanks_to_maternal.sh           # Align flanks to maternal
├── align_flanks_to_paternal.sh           # Align flanks to paternal
├── analyze_flank_alignments.py           # Analyze MAPQ distribution
└── filter_paired_flanks.py               # Filter for properly paired flanks
```

### Workflow

#### Step 1: Extract Flanking Regions
```bash
python scripts/repeat_sizing/extract_flanking_regions.py \
    catalogs/catalog_repeat_regions_HG002_GRCH38_Tier1.bed \
    data/hg38.fa \
    data/hg002_repeat_region_flanks.fa \
    --flank-size 250
```

Extracts 250bp flanking regions on each side of repeat regions.

#### Step 2: Split Haplotype-Resolved Assembly
```bash
cd scripts
./log_job.sh repeat_sizing/split_haplotypes.sh
```

Splits `hg002v1.1.fasta.gz` into:
- `data/hg002v1.1_maternal.fasta.gz` (chromosomes ending in `_MATERNAL` + chrM)
- `data/hg002v1.1_paternal.fasta.gz` (chromosomes ending in `_PATERNAL`)

#### Step 3: Build Minimap2 Indexes (Parallel)
```bash
cd scripts
./log_job.sh repeat_sizing/build_maternal_minimap2_index.sh
./log_job.sh repeat_sizing/build_paternal_minimap2_index.sh
```

Creates `.mmi` index files for fast alignment.

#### Step 4: Align Flanking Regions (Parallel)
```bash
cd scripts
./log_job.sh repeat_sizing/align_flanks_to_maternal.sh
./log_job.sh repeat_sizing/align_flanks_to_paternal.sh
```

Produces:
- `data/flanks_maternal.sam` - Alignments to maternal chromosomes (~750MB)
- `data/flanks_paternal.sam` - Alignments to paternal chromosomes (~750MB)

#### Step 5: Filter High-Quality Alignments (MAPQ=60)
```bash
# Keep only uniquely mapped flanks (MAPQ=60)
awk 'BEGIN {OFS="\t"} /^@/ || $5==60' data/flanks_maternal.sam > data/flanks_maternal_high_quality.sam
awk 'BEGIN {OFS="\t"} /^@/ || $5==60' data/flanks_paternal.sam > data/flanks_paternal_high_quality.sam
```

Filters out ~16% of alignments with MAPQ=0 (multi-mapped/ambiguous).

#### Step 6: Analyze Alignment Quality (Optional)
```bash
cd scripts
python repeat_sizing/analyze_flank_alignments.py \
    ../data/flanks_maternal.sam \
    ../data/flanks_paternal.sam
```

Generates MAPQ distribution plots and statistics.

#### Step 7: Filter for Properly Paired Flanks
```bash
cd scripts
python repeat_sizing/filter_paired_flanks.py ../data/flanks_maternal_high_quality.sam
python repeat_sizing/filter_paired_flanks.py ../data/flanks_paternal_high_quality.sam
```

Keeps only repeats where:
- Both left (LF) and right (RF) flanks are present
- Both flanks map to the same chromosome
- Mapped chromosome matches expected chromosome from repeat ID

Produces:
- `data/flanks_maternal_filtered.sam` - Paired, high-quality maternal alignments
- `data/flanks_paternal_filtered.sam` - Paired, high-quality paternal alignments

#### Step 8: Calculate Repeat Sizes (In Development)
Parse filtered SAM files to calculate repeat sizes for each haplotype.

### Resource Requirements

| Script | Memory | CPUs | Partition | Runtime |
|--------|--------|------|-----------|---------|
| split_haplotypes.sh | 400GB | 1 | bigmem | ~30 min |
| build_*_minimap2_index.sh | 384GB | 64 | bigmem | ~1 min |
| align_flanks_to_*.sh | 384GB | 64 | bigmem | ~26 sec |
| analyze_flank_alignments.py | - | - | login node | ~1-2 min |
| filter_paired_flanks.py | - | - | login node | <1 min |

### Input Data

- **Reference genome**: `data/hg38.fa` (GRCh38)
- **Repeat catalog**: `catalogs/catalog_repeat_regions_HG002_GRCH38_Tier1.bed`
- **Phased assembly**: `data/hg002v1.1.fasta.gz` (haplotype-resolved HG002)

### Output Data

- Flanking sequences: `data/hg002_repeat_region_flanks.fa`
- Haplotype assemblies: `data/hg002v1.1_{maternal,paternal}.fasta.gz`
- Minimap2 indexes: `data/hg002v1.1_{maternal,paternal}.mmi`
- SAM alignments (all): `data/flanks_{maternal,paternal}.sam`
- High-quality SAM (MAPQ=60): `data/flanks_{maternal,paternal}_high_quality.sam`
- Filtered SAM (paired flanks): `data/flanks_{maternal,paternal}_filtered.sam`
- MAPQ analysis plots: `data/flank_alignment_analysis_mapq_distribution.png`

## Notes

- Scripts use relative paths assuming execution from `scripts/` directory
- Large data files (FASTQ, BAM, etc.) are excluded from git tracking
- See `CLAUDE.md` for detailed project conventions