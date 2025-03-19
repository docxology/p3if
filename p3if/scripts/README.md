# P3IF Scripts

This directory contains executable scripts for the P3IF framework.

## Available Scripts

- **run_multidomain_portal.py** - Generates a visualization portal with a domain selector
- **generate_visualizations.sh** - Batch script to generate visualizations for all domains

## Usage

### Run Multi-Domain Portal

```bash
# From project root
python3 p3if/scripts/run_multidomain_portal.py --output-dir output

# For help with options
python3 p3if/scripts/run_multidomain_portal.py --help
```

### Generate All Visualizations

```bash
# From project root
bash p3if/scripts/generate_visualizations.sh
```

Both scripts will output to the `/output` directory at the project root. 