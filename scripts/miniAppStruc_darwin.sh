#!/bin/bash
#SBATCH -N 2
#SBATCH --ntasks-per-node 8
#SBATCH -p galton

export MPIP="-t 10.0"
projectpath=/projects/insituperf/InSituWriters
pythonExe=/home/pascalgrosset/miniconda3/bin/python

# init spack
export SPACK_ROOT=$HOME/spack
source $SPACK_ROOT/share/spack/setup-env.sh

# load modules
source $projectpath/InWrap/scripts/env_setup_darwin.sh
source $projectpath/InWrap/scripts/env_setup_spack.sh


module list

# Get IP
nodes=$(scontrol show hostnames $SLURM_JOB_NODELIST) # Getting the node names
nodes_array=( $nodes )
node1=${nodes_array[0]}

ip=$(srun --nodes=1 --ntasks=1 -w $node1 hostname --ip-address)
echo $ip



# Create 
mpirun $pythonExe $projectpath/InWrap/python-utils/createJson.py $ip $projectpath/InWrap/inputs/input-test-structured.json


# Execute jobs in parallel: server + demoApp
mpirun $pythonExe $projectpath/InWrap/python-utils/launchServer.py $projectpath/InWrap/inputs/input-test-structured.json &
mpirun $projectpath/build/demoApps/miniAppStructured --insitu $projectpath/InWrap/inputs/input-test-structured.json

## Terminate the server
mpirun $pythonExe $projectpath/InWrap/python-utils/shutDownServer.py $projectpath/InWrap/inputs/input-test-structured.json 
