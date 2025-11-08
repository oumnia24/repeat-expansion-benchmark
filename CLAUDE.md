# Project Conventions for Repeat Expansion Benchmark

## Directory Structure
```
/scratch/users/oumnia/repeat-expansion-benchmark/
├── scripts/       # All SLURM job scripts
├── data/          # Input data (FASTQ, reference genomes)
├── results/       # Output from analyses
└── callers/       # Repeat expansion caller software
```

## Script Execution Rules

### IMPORTANT: All scripts must be run from within the scripts/ directory

1. **Always submit jobs from the scripts directory:**
   ```bash
   cd /scratch/users/oumnia/repeat-expansion-benchmark/scripts
   sbatch script_name.sh
   ```

2. **Use relative paths in scripts:**
   - Data files: `../data/filename`
   - Results: `../results/filename`
   - Callers: `../callers/program`

3. **Example script structure:**
   ```bash
   #!/bin/bash
   #SBATCH directives...
   
   # Change to project root
   cd ..
   
   # Now use paths relative to project root
   minimap2 -d data/hg38.mmi data/hg38.fa
   ```

## Sherlock-Specific Conventions

- Default partition: `normal`
- Module loading: Always load required modules (e.g., `module load biology minimap2`)
- Output logs: Use `%j` in filenames for job ID tracking

## Data Conventions

- Reference genome: `data/hg38.fa`
- HG002 samples: Store in `data/` with descriptive names
- Benchmark files: Keep in `data/benchmarks/`