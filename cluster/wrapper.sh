#!/bin/bash
set -e -f  #Fail on error and disable globbing
set -- $SSH_ORIGINAL_COMMAND  #Parse CMD args to $1 $2 ... $n
#echo viwa_prepare_runs.r --phenology_factor "$1" --nutrition_factor "$2" --irrigation "$3" --seeding_date "$4" 

if [ "$1" == "submit" ]; then
	module load r
	cd $WORK/viwa_process/preprocessing
	Rscript viwa_prepare_runs.r --phenology_factor "$2" --nutrition_factor "$3" --irrigation "$4" --seeding_date "$5" --id "$6"
	cd $WORK/viwa_process/workspaces/Workspace_01_SAM_South_America
	sbatch runbatch_ws01_sam_maize_nutr060_seedorg.slurm  
elif [ "$1" == "status" ]; then
	squeue --clusters "$2" --job "$3"
elif [ "$1" == "check" ]; then
	sacct -X -P --cluster "$2" --jobs "$3" --format=User,JobID,Jobname,partition,state,time,start,end,elapsed,MaxRss,MaxVMSize,nnodes,ncpus,nodelist
elif [ "$1" == "collect" ]; then
	module load r
	cd $WORK/viwa_process/postprocessing/merging
	Rscript viwa_merging.r --phenology_factor "$2" --nutrition_factor "$3" --irrigation "$4" --seeding_date "$5" --id "$6"
	sbatch "merge_${6}.slurm"
elif [ "$1" == "archive" ]; then
	module load r
	cd $WORK/viwa_process/postprocessing/archiving
	Rscript viwa_archiving.r --phenology_factor "$2" --nutrition_factor "$3" --irrigation "$4" --seeding_date "$5" --id "$6"
	sbatch "archive_${6}.slurm"
else
	echo "Error: please use 'submit', 'status', 'collect' or 'check'" >&2
	exit 1
fi
exit 0
