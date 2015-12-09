from optparse import OptionParser
import numpy as np
import math

def target_to_values(output_loc, log_tpm=False):
    """
    Args:
        output_loc: Location of Kallisto output
    Returns:
        target_to_values: A dictionary mapping
            a target's ID to a dictionary that maps
            a value type to its value. Value types
            include "tpm", "est_counts"
    """
    print "Parsing %s" % output_loc 
    target_to_data = {}
    with open(output_loc, "r") as f:
        lines = f.readlines()
        col_labels = [x.strip() for x in lines[0].split()]
        for line in lines[1:]:
            tokens = [x.strip() for x in line.split()]
            target_id = tokens[0]
            target_to_data[target_id] = {}
            for i in range(1, len(col_labels)):
                if tokens[i] == "-nan":
                    raise TypeError("TPM value in %s is NaN!" % output_loc)
                target_to_data[target_id][col_labels[i]] = float(tokens[i])
    return target_to_data

def tpm_vector(output_loc, log_tpm=False):
    """
    Args:
        output_loc: Location of Kallisto output
    Returns:
        tpm: a vector of TPM for each target
        counts: a vector of the number of reads 
            aligning to each target
        targets: a list of targets in the same
            order as the tpm and counts vectors
    """
    target_to_data = target_to_values(output_loc)
    tpm_vector = []
    counts_vector = []
    targets = []
    for target_id in target_to_data.keys():
        if log_tpm:
            tpm_vector.append( math.log(target_to_data[target_id]["tpm"] + 1.0) )
        else:
            tpm_vector.append( target_to_data[target_id]["tpm"] )
    return np.array(tpm_vector)

def main():
    parser = OptionParser()
    (options, args) = parser.parse_args()
    kallisto_out = args[0] 
    vectors(kallisto_out) 

if __name__ == "__main__":
    main()
