#!/usr/bin/python

import xml.etree.ElementTree as et
import urllib2
import os
from os.path import join, dirname
import sys
import random
import time

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.append( join(get_script_path(), "../../common") )

# GEO query
BASE_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
DB = "sra"

# GEO XML record
XML_RUNS_PATH = "EXPERIMENT_PACKAGE/RUN_SET"
XML_RUN_ACCESION_ATTR = "accession"

# Parallel downloading
NUM_DOWNLOAD_SLOTS = 5

# Aspera 
TRANSFER_RATE = 640
ASPERA_KEY = "%s/bin/aspera/asperaweb_id_dsa.openssh" % get_script_path()
ASPERA_BIN = join(get_script_path(), "bin", "aspera", "ascp")

# Download locations
FINAL_FASTQ_DIRNAME = "fastq"
DOWNLOADED_FASTQ_DIRNAME = "downloaded_fastq"

# log
LOG_PATH = "./fetch_fastq.log"

SRA_FILE_LOCATION_PREFIX = "anonftp@ftp.ncbi.nlm.nih.gov:/sra/sra-instant/reads/ByRun/sra"

def main():
    script_path = get_script_path()
    records_root = "/tier2/deweylab/mnbernstein/sra_metadata/human_rna_seq_experiment_records"
    
    relavent = sys.argv[1].split(",")
    print relavent
        
    records = []
    for l1_dir in sorted(os.listdir(records_root)):
        for record in os.listdir(join(records_root, l1_dir)):
            if record.split(".")[0] in relavent:
                record_path = join(records_root, l1_dir, record)
                records.append(parse_record(record_path))

    total_size = 0 
    for record in records:
        total_size += record["total_size_sra"]
    print "Total size of data (GB): %f" % (total_size / 1000000000.0) 

def parse_record(exp_xml):
    """
    For a given GEO experiment ID, retrieve all SRA accessions for that
    experiment.
    """
    exp_info = {}
    #print "Record %s" % exp_xml
    sizes = []
    run_accessions = []
    tree = et.parse(exp_xml)
    root = tree.getroot()
    if root.findall("ERROR"):
        exp_info["public"] = False
        return exp_info    
    for run in root.find(XML_RUNS_PATH):
        run_accessions.append(run.get("accession"))
        if (not run.get("accession")) and run.get("size"):
            print "NO ACC BUT SIZE %s" % exp_xml 
        if run.get("size"):
            sizes.append(int(run.get("size")))
    exp_info["public"] = True
    exp_info["run_accessions"] = run_accessions
    if sizes:
        exp_info["total_size_sra"] = sum(sizes)
    else:
        exp_info["total_size_sra"] = None
    return exp_info

#def retrieve_run_accession_size(exp_xml):
#    """
#    For a given GEO experiment ID, retrieve all SRA accessions for that
#    experiment.
#    """
#    accessions = []
#    tree = et.parse(exp_xml)
#    root = tree.getroot()
#    for run in root.find(XML_RUNS_PATH):
#        accessions.append(run.get(XML_RUN_ACCESION_ATTR))
#    return accessions

if __name__ == "__main__":
    main()
