#!/bin/bash
#SBATCH -p main           # use the 'cpu' partition
#SBATCH -n8               # request 8 CPU cores
#SBATCH -t 24:00:00       # up to 24 hour of runtime
#SBATCH -J bda_assignment_1     # job name
#SBATCH -o bda_assignment_1.out # output file name

python3 main.py