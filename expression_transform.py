from optparse import OptionParser
import sqlite3
import subprocess
import os
from os.path import join

import parse_kallisto

repo_loc = "/tier2/deweylab/mnbernstein/quantified_samples"
output_loc = "/scratch/mnbernstein/CS706_repo"

def experiment_to_target_to_values(exp_list_file, params_hash):
    print "Gathering data from experiments listed in '%s'..."  % exp_list_file
    exp_accs = []
    with open(exp_list_file, 'r') as f:
        exp_accs = f.readlines()[0].strip().split(",")

    exp_acc_to_target_to_values = {}
    for exp_acc in exp_accs:
        out_loc = join(repo_loc, exp_acc, params_hash, "gene_tpm.tsv")
        exp_acc_to_target_to_values[exp_acc] = parse_kallisto.target_to_values(out_loc)
    return exp_acc_to_target_to_values

def transform_to_boolean(exp_list_file, params_hash):
    
    exp_to_target_to_values = experiment_to_target_to_values(exp_list_file, params_hash)
    for experiment, target_to_values in exp_to_target_to_values.iteritems():
        for target, values in target_to_values.iteritems():
            if values["tpm"] > 1.0:
                values["bool_expressed"] = 1
            else:
                values["bool_expressed"] = 0

    for experiment, target_to_values in exp_to_target_to_values.iteritems():
        out_dir = join(output_loc, experiment)
        run_command("mkdir %s" % out_dir)
        with open(join(out_dir, "gene_bool_express.tsv"), 'w') as f:
            f.write("gene\tis_expressed\n")
            targets = sorted(target_to_values.keys()) # Ensure targets are visited in a consistent order
            for target in targets: 
                is_expressed = target_to_values[target]["bool_expressed"]
                f.write("%s\t%s\n" % (target, is_expressed))
            


def run_command(cmd):
    subprocess.call(cmd, shell=True, env=None)

def main():
    parser = OptionParser()
    #parser.add_option("-a", "--a_descrip", action="store_true", help="This is a flat")
    parser.add_option("-b", "--transform_to_bool", action="store_true", help="Transform gene expression to Boolean expression")
    (options, args) = parser.parse_args()
    
    exp_list_file = args[0]
    params_hash = args[1]

    if options.transform_to_bool:
        transform_to_boolean(exp_list_file, params_hash)
    

if __name__ == "__main__":
    main()
