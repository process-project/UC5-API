"""Utility module for common not state dependent functions"""
import re

def parse_slurm_output(string):
    """Parses the output of slurm sbatch command into slurm job id and cluster name"""
    job_id = None
    cluster = None
    regex = 'Submitted batch job ([0-9]+) on cluster ([a-zA-Z0-9]+).*'
    regex = re.search(regex, string)
    if regex:
        job_id = regex.group(1)
        cluster = regex.group(2)
    else:
        return (-1, '')

    return(int(job_id), str(cluster))

def parse_sacct_output(string):
    """Parses the output of slurm sacct command into a dict

        The sacct command needs to be printed with -P flag enabled
    """
    delim = '|'
    result = {}
    string = string.split("\n")
    if len(string) <= 1:
        return result
    header = string.pop(0).split(delim)
    for line in string:
        if len(line) == 0:
            continue
        split_line = line.split(delim)
        data = {header[i] : str(split_line[i]) for i in range(len(header))}
        result[str(split_line[1])] = data

    return result
