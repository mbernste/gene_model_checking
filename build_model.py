from optparse import OptionParser
import json
from sets import Set
import sys
import os
from os.path import join
import parse_kallisto
import pygraphviz as pgv

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

import go

GO_OBO_LOC = "/go/go.obo"
GENE_TO_GO_LOC = "/go/gene_to_GO_term.txt"
REPO_LOC = "/scratch/mnbernstein/CS706_repo"

class Model:
    def __init__(self, nodes, edges, labels):
        self.nodes = nodes
        self.edges = edges
        self.labels = labels

class ModelBuilder:
    def __init__(self, meta_files):
        self.node_to_adj = None 

        # Build the initial graph
        self.origin_node_to_adj = build_premerge_graph(meta_files)

        self.all_nodes = []
        for node_to_adj_list in self.origin_node_to_adj:
            self.all_nodes += list(node_to_adj_list.keys())

        # Load the data
        self.exp_to_gene_to_targ_to_vals = experiment_to_target_to_values(self.all_nodes)

    def build(self, gene_set):
        # Build atomic propositions for each node
        node_to_adjs = list(self.origin_node_to_adj)
        node_to_props = node_to_atomic_propositions(self.all_nodes, gene_set, self.exp_to_gene_to_targ_to_vals)

        # Compress premerged graphs
        node_to_adjs, node_to_props = compress_graphs(node_to_adjs, node_to_props)

        # Map each node to a connected component ID
        node_to_component = map_nodes_to_components(node_to_adjs)

        # Merge graphs
        m_node_to_adjs = merge_graphs(node_to_adjs, node_to_props, node_to_component)

        return Model(m_node_to_adjs.keys(), m_node_to_adjs, node_to_props)

    def dot_file(self):
        g = pgv.AGraph(directed='True')
        if len(self.node_to_adj) == 1:
            g.add_node(list(self.node_to_adj.keys())[0])
        else:
            for s_node, adj_list in self.node_to_adj.iteritems():
                for t_node in adj_list:
                    g.add_edge(s_node, t_node)
        return str(g)


def main():
    parser = OptionParser()
    #parser.add_option("-a", "--a_descrip", action="store_true", help="This is a flat")
    #parser.add_option("-b", "--b_descrip", help="This is an argument")
    (options, args) = parser.parse_args()
    
    meta_files = args[0].split(",")

    m = ModelBuilder(meta_files)
    m.build(['ENSG00000009830', 'ENSG00000086848', 'ENSG00000130714', 'ENSG00000253710', 'ENSG00000132581', 'ENSG00000136908', 'ENSG00000189366', 'ENSG00000060642', 'ENSG00000214160', 'ENSG00000178904', 'ENSG00000000419', 'ENSG00000179085', 'ENSG00000119523', 'ENSG00000119227', 'ENSG00000173852', 'ENSG00000069943', 'ENSG00000177990', 'ENSG00000182858', 'ENSG00000159063', 'ENSG00000033011', 'ENSG00000156162'])

    with open("merged_model.dot", "w") as f:
        f.write( m.dot_file() )

def duh():

    # Build the initial graph
    node_to_adj_lists = build_premerge_graph(meta_files)

    all_nodes = []
    for node_to_adj_list in node_to_adj_lists:
        all_nodes += list(node_to_adj_list.keys())

    # Load the data
    exp_to_gene_to_targ_to_vals = experiment_to_target_to_values(all_nodes)
    
    #print_graph(node_to_adj_lists[0])
    #n, m = merge_nodes("SRX129998","SRX130001", node_to_adj_lists[0])
    #print_graph(n)    

    #node_to_adj_list = merge_nodes("SRX130000", "SRX130007",node_to_adj_list) 
    #print "MERGED"
    #print_graph(node_to_adj_list)

    test_gene_set = ['ENSG00000009830', 'ENSG00000086848', 'ENSG00000130714', 'ENSG00000253710', 'ENSG00000132581', 'ENSG00000136908', 'ENSG00000189366', 'ENSG00000060642', 'ENSG00000214160', 'ENSG00000178904', 'ENSG00000000419', 'ENSG00000179085', 'ENSG00000119523', 'ENSG00000119227', 'ENSG00000173852', 'ENSG00000069943', 'ENSG00000177990', 'ENSG00000182858', 'ENSG00000159063', 'ENSG00000033011', 'ENSG00000156162']

    # Build atomic propositions for each node
    node_to_props = node_to_atomic_propositions(all_nodes, test_gene_set, exp_to_gene_to_targ_to_vals) 

    # Compress premerged graphs
    node_to_adj_lists, node_to_props = compress_graphs(node_to_adj_lists, node_to_props)

    print "LEN %d" % len(node_to_adj_lists)

    # Map each node to a connected component ID
    node_to_component = map_nodes_to_components(node_to_adj_lists)

    # Merge graphs
    m = merge_graphs(node_to_adj_lists, node_to_props, node_to_component)
    m.build(test_gene_set)
    
    print_graph(m) 


def map_nodes_to_components(node_to_adjs):
    component_id = 1
    node_to_component = {}
    for node_to_adj in node_to_adjs:
        for node in node_to_adj:
            node_to_component[node] = component_id
        component_id += 1
    return node_to_component

def merge_graphs(node_to_adjs, node_to_props, node_to_component):
    
    # Initialize graphs into one graph
    m_node_to_adj = {}
    for node_to_adj in node_to_adjs:
        for node, adj in node_to_adj.iteritems():
            m_node_to_adj[node] = adj

    merged = True
    while merged:
        merged = False
        for node_i in m_node_to_adj:
            for node_j in m_node_to_adj:
            
                # If neither node is mapped to a component then this node
                # represents a merged node between two components
                if node_i not in node_to_component and node_j not in node_to_component:
                    continue
                
                # If both nodes belong to the same component, do not merge them
                if node_i in node_to_component and node_j in node_to_component:
                    if node_to_component[node_i] == node_to_component[node_j]:
                        continue

                # If two nodes have same atomic propositions, then merge them 
                if Set(node_to_props[node_i]) == Set(node_to_props[node_j]):
                        m_node_to_adj, merged_node = merge_nodes(node_i, node_j, m_node_to_adj)
                        node_to_props[merged_node] = node_to_props[node_i]
                        node_to_props.pop(node_i, None)
                        node_to_props.pop(node_j, None)
                        merged = True
                        break

            if merged:
                break

    return m_node_to_adj

def merge_graphs_ORIGINAL_MESSY(node_to_adj_lists, node_to_props): 
    print "Merging graphs..."

    popped_nodes = Set()

    m_node_to_adj_list = node_to_adj_lists[0]
    for i in range(1, len(node_to_adj_lists)): # Iterate over all connected components
        print "Examining connected component."
        merged = True
        # Keep merging nodes from the current connect component
        # to the current merged graph
        while merged: 
            merged = False

            # Iterate over all nodes in the two connected components searching for two
            # nodes that should be merged
            for node_m in m_node_to_adj_list:
                for node_c in node_to_adj_lists[i]:
                    if node_c in popped_nodes:
                        continue
                    if Set(node_to_props[node_m]) == Set(node_to_props[node_c]):
                        m_node_to_adj_list[node_c] = [x for x in node_to_adj_lists[i][node_c] if x not in popped_nodes]
                        m_node_to_adj_list, merged_node = merge_nodes(node_m, node_c, m_node_to_adj_list)
                        node_to_props[merged_node] = node_to_props[node_m]
                        node_to_props.pop(node_m, None)
                        node_to_props.pop(node_c, None)
                        popped_nodes.add(node_c)
                        merged = True
                        break
                if merged:
                    break

    return m_node_to_adj_list



def compress_graphs(node_to_adj_lists, node_to_props):
    """
    Compress each connected component in the premerge graph.
    Adjacent nodes are merged into a single node if they contain
    the same atomic propositions.
    Args:
        node_to_adj_lists: a list of maps where each map is
            maps a node to its adjacency list and represents
            a single connected component
        node_to_props: maps each node to the set of atomic
            propositions at the node
    """
    print "Compressing connected components..."
    c_node_to_adj_lists = []
    for node_to_adj_list in node_to_adj_lists:
        c_node_to_adj_list = dict(node_to_adj_list)
        merged = True
        while merged: # Keep merging until no nodes have been merged
            merged = False
            for s_node in c_node_to_adj_list:
                for t_node in c_node_to_adj_list[s_node]:
                    if Set(node_to_props[s_node]) == Set(node_to_props[t_node]):
                        c_node_to_adj_list, merged_node = merge_nodes(s_node, t_node, c_node_to_adj_list)
                        node_to_props[merged_node] = node_to_props[s_node]
                        node_to_props.pop(s_node, None)
                        node_to_props.pop(t_node, None)
                        merged = True
                        break
                if merged:
                    break
        c_node_to_adj_lists.append(c_node_to_adj_list)
    print "Finished."
    return c_node_to_adj_lists, node_to_props
       
 

def build_premerge_graph(meta_files):    

    node_to_adj_lists = []
    nodes = []
    
    for m_f in meta_files:
        with open(m_f, 'r') as f:
            print m_f
            meta_info = json.load(f)
            all_exps = meta_info["experiments"]
            
            # Add all experiments to the node list
            for exp in all_exps:
                nodes.append(exp["accession"])

            # Create a connected component for each biological replicate
            for replicate, order in meta_info["replicate_to_order"].iteritems():
                node_to_adj_list = {}
                r_exps = [x for x in all_exps if x["biological_replicate"]==replicate]
                
                # Assign node to its component
                for x in r_exps:
                    node = x["accession"]
                    node_to_adj_list[node] = Set()

                for i in range(0,len(order)-1):
                    t  = order[i]
                    t_next = order[i+1]
                    nodes_t = [x["accession"] for x in r_exps if x["time_point"] == t]       
                    nodes_t_next = [x["accession"] for x in r_exps if x["time_point"] == t_next] 
                    for exp_t in nodes_t:
                        for exp_t_next in nodes_t_next:
                            node_to_adj_list[exp_t].add(exp_t_next)
                node_to_adj_lists.append(node_to_adj_list)
   
    return node_to_adj_lists



def node_to_atomic_propositions(nodes, gene_set, exp_to_gene_to_targ_to_vals):
    node_to_propositions = {}
    for node in nodes:
        node_to_propositions[node] = []
        for gene in gene_set:
            if gene not in exp_to_gene_to_targ_to_vals[node]:
                print "Warning. Gene %s is not in the expression data."
                continue
            node_to_propositions[node].append( gene_atomic_proposition(gene, int(exp_to_gene_to_targ_to_vals[node][gene]['is_expressed']) ) )
    return node_to_propositions



def gene_atomic_proposition(gene, expression):
    return "%s_%s" % (gene, str(expression))



def merge_nodes(s_node, t_node, node_to_adj_list):
    """
    Given the premereged graph, merge two adjacent nodes.
    """
    print "Merging nodes %s and %s" % (s_node, t_node)

    # Create merged node
    m_node = "%s__%s" % (s_node, t_node)
    s_adj = Set(node_to_adj_list[s_node])
    t_adj = Set(node_to_adj_list[t_node])
    if t_node in s_adj:
        s_adj.remove(t_node)
    if s_node in t_adj:
        t_adj.remove(s_node)
    m_node_adj_list = s_adj.union(t_adj)

     # Remove s_node and t_node from adjacency lists
    node_to_adj_list.pop(s_node, None)
    node_to_adj_list.pop(t_node, None)

    # Remove s_node and t_node from all nodes' adjacency lists
    for node, adj_list in node_to_adj_list.iteritems():
        if node == s_node or node == t_node:
            continue
        if s_node in node_to_adj_list[node]:
            node_to_adj_list[node].remove(s_node)
            node_to_adj_list[node].add(m_node)
        if t_node in node_to_adj_list[node]:
            node_to_adj_list[node].remove(t_node)
            node_to_adj_list[node].add(m_node)    

    # Add new node to adjacency lists
    node_to_adj_list[m_node] = m_node_adj_list
    return node_to_adj_list, m_node


    
def experiment_to_target_to_values(exps):
    exp_to_targ_to_vals = {}
    for exp in exps:
        out_loc = join(REPO_LOC, exp, "gene_bool_express.tsv")
        exp_to_targ_to_vals[exp] = parse_kallisto.target_to_values(out_loc)
    return exp_to_targ_to_vals



def print_graph(node_to_adj_list):
    for node, adj_list in node_to_adj_list.iteritems():
        print "%s --> %s" % (node, str(adj_list))
        print   

if __name__ == "__main__":
    main()