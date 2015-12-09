from optparse import OptionParser
from sets import Set

import ontology_graph as ont_graph

class GeneOntology:
    def __init__(self, ontology_graph, go_to_genes):
        self.og = ontology_graph    
        self.go_to_genes = go_to_genes

    def genes_for_go_term_id(self, go_term):
        subterms = self.og.recursive_subterms(root_id=go_term)
        genes = Set()
        for term in subterms: 
            if term.id in self.go_to_genes:
                genes.update(self.go_to_genes[term.id])
        return genes    
                    
def build_go_ontology(gene_to_go_f, go_obo_f):
    go_ontology_graph = ont_graph. parse_obo(go_obo_f)
    go_to_genes = build_go_to_genes(gene_to_go_f)
    return GeneOntology(go_ontology_graph, go_to_genes)

def build_go_to_genes(gene_to_go_f):
    go_to_genes = {}
    with open(gene_to_go_f, 'r') as f:
        for line in f.readlines():
            tokens = line.strip().split(",")
            gene = tokens[0]
            go_term = tokens[1]
            if go_term not in go_to_genes:
                go_to_genes[go_term] = []
            go_to_genes[go_term].append(gene)
    return go_to_genes

def main():
    parser = OptionParser()
    #parser.add_option("-a", "--a_descrip", action="store_true", help="This is a flat")
    #parser.add_option("-b", "--b_descrip", help="This is an argument")
    (options, args) = parser.parse_args()
    
    gene_to_go_f = args[0]
    go_obo_f = args[1]
    go = build_go_ontology(gene_to_go_f, go_obo_f)
    
    print go.genes_for_go_term_id("GO:0000030")

if __name__ == "__main__":
    main()
