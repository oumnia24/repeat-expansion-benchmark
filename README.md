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

## Notes

- Scripts use relative paths assuming execution from `scripts/` directory
- Large data files (FASTQ, BAM, etc.) are excluded from git tracking
- See `CLAUDE.md` for detailed project conventions