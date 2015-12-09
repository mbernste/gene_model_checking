from optparse import OptionParser
from easygui import *
import os
from os.path import join
import sys
import subprocess
import ctl

import go
import build_model

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

GENE_TO_GO = join(get_script_path(), "..", "go", "gene_to_GO_term.txt")
GO_OBO = join(get_script_path(), "..", "go", "go.obo")
META_FILES = [join("..", "metadata", "SRP011546", "SRP011546.json"),
    join("..", "metadata", "SRP041179", "SRP041179.json")]

 
def main():
    parser = OptionParser()
    #parser.add_option("-a", "--a_descrip", action="store_true", help="This is a flat")
    #parser.add_option("-b", "--b_descrip", help="This is an argument")
    (options, args) = parser.parse_args()

    #meta_files = args[0].split(",")


    go_graph = go.build_go_ontology(GENE_TO_GO, GO_OBO)
    name_to_termid = {x[1].name : x[0] for x in go_graph.og.id_to_term.iteritems()}

    model_builder = build_model.ModelBuilder(META_FILES)

    curr_mode = None
    while 1:
        inp = raw_input("$>")
        t = inp.split()
        print t
        if t[0] == "nm":
            curr_mod = model_builder.build(go_graph.genes_for_go_term_id(name_to_termid[" ".join(t[1:])]))
            with open("current_model.dot", "w") as f:
                f.write(model_builder.dot_file())
            run_command("dot -Tpng ./current_model.dot -o current_model.png")
            
        elif t[0] == "qu":
            if curr_mod is None:
                print "No constructed model exists. Build a model with the 'nm' command."
                continue
            ctl_q = " ".join(t[1:])
            try:
                print ctl.check(curr_mod, ctl_q)   
            except Exception as e:
                print e    
        elif t[0] == "ge":
            if curr_mod is None:
                print "No constructed model exists. Build a model with the 'nm' command."
                continue
            print "Model's gene set: %s" % str(curr_mod.gene_set) 
        elif t[0] == "ed":
            print "Current model adjacency lists:\n%s" % str(curr_mod.edges)

def open_gui():
    while 1:
        title = "Choose gene set."
        choices = list(name_to_termid.keys())
        msg = "Choose a GO term from which to build the model:"
        choice = choicebox(msg, title, choices, wid=300, hei=200)
        print choice

        model_builder.build(go_graph.genes_for_go_term_id(name_to_termid[choice]))
        with open("current_model.dot", "w") as f:
            f.write(model_builder.dot_file())
    
        run_command("dot -Tpng ./current_model.dot -o current_model.png")
        run_command("cp current_model.png current_model_original.png")
        run_command("convert current_model.png -resize 2000x1000 current_model.png")
        run_command("convert current_model.png current_model.gif")

        msg = "The constructed model structure."
        choices = ["Continue"]
        reply=buttonbox(msg, image="current_model.gif", choices=choices)

        msg = "Do you want to continue?"
        title = "Please Confirm"
        if ccbox(msg, title):     # show a Continue/Cancel dialog
            pass  # user chose Continue
        else:
            sys.exit(0)           # user chose Cancel


def run_command(cmd, tag=None, env=None):
    subprocess.call(cmd, shell=True, env=env)


if __name__ == "__main__":
    main()


