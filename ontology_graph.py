#!/usr/bin/python

import re
import pygraphviz as pgv
from optparse import OptionParser
from Queue import Queue
from sets import Set

ENTITY_TERM = "TERM"
SYNONYM_RELATIONS = ["EXACT", "RELATED"]

class Term:
    def __init__(self, id, name, definition=None, synonyms=[], is_a=None, inv_is_a=None):
        self.id = id
        self.name = name
        self.definition = definition
        self.synonyms = synonyms
        self.is_a = Set() if not is_a else is_a       
        self.inv_is_a = Set() if not inv_is_a else inv_is_a
    
    def __repr__(self):
        rep = {"id":self.id, "name":self.name, "definition":self.definition, "synonyms":self.synonyms, "is_a":self.is_a, "inv_is_a":self.inv_is_a}
        return str(rep)

class OntologyGraph:
    def __init__(self, id_to_term, name_to_id):
        self.id_to_term = id_to_term
        self.name_to_id = name_to_id
        self.synonym_to_term = self.__build_synonym_to_term()

    def __build_synonym_to_term(self):
        syn_to_term = {}
        for term in self.id_to_term.values():
            if len(term.synonyms) > 0:
                for synonym in term.synonyms:
                    syn_to_term[synonym] = term
        return syn_to_term   

    def subtype_names(self, supertype_name):
        id = self.name_to_id[supertype_name]
        for t in self.id_to_term[id].inv_is_a:
            print self.id_to_term[t].name

    def graphviz(self, root_id=None):
        g = pgv.AGraph(directed='True')               
        
        # Breadth-first traversal from root
        visited_ids = Set()
        curr_id = root_id
        q = Queue()
        q.put(curr_id)
        while not q.empty():
            curr_id = q.get()
            visited_ids.add(curr_id)                    
            for sub_id in self.id_to_term[curr_id].inv_is_a:
                if not sub_id in visited_ids:
                    g.add_edge(self.id_to_term[curr_id].name, self.id_to_term[sub_id].name)
                    q.put(sub_id)
        print str(g)
     
    def direct_subterms(self, id):
        return Set([self.id_to_term[x] for x in self.id_to_term[id].inv_is_a])

    def recursive_subterms(self, root_id=None):
        subterms = Set()
        curr_id = root_id
        q = Queue()
        q.put(curr_id)
        visited_ids = Set()
        while not q.empty():
            curr_id = q.get()
            visited_ids.add(curr_id)
            subterms.add(self.id_to_term[curr_id])
            for sub_id in self.id_to_term[curr_id].inv_is_a:
                if not sub_id in visited_ids:
                    q.put(sub_id) 
        return subterms
    
    def recursive_superterms(self, id):
        superterms = Set()
        curr_id = id
        q = Queue()
        q.put(curr_id)
        visited_ids = Set()
        while not q.empty():
            curr_id = q.get()
            visited_ids.add(curr_id)
            superterms.add(self.id_to_term[curr_id])
            for sup_id in self.id_to_term[curr_id].is_a:
                if not sup_id in visited_ids:
                    q.put(sup_id)
        return superterms

def main():
    parser = OptionParser()
    (options, args) = parser.parse_args()

    obo_file = args[0]
    og = parse_obo(obo_file)

    print str([x.name for x in og.direct_subterms(og.name_to_id["brain cancer"])])
    print str([x.name for x in og.recursive_subterms(og.name_to_id["brain cancer"])])
        
    #og.graphviz(ontology_graph.name_to_id["breast cancer"])

def parse_obo(obo_file):
    header_info = {}

    name_to_id = {}
    id_to_term = {}
    with open(obo_file, 'r') as f:
        for line in f:
            if not line.strip():
                break # Reached end of header
            header_info[line.split(":")[0].strip()] = ":".join(line.split(":")[1:]).strip()

        curr_lines = []
        for line in f:
            if not line.strip():
                entity = parse_entity(curr_lines)
                if not entity:
                    continue
                if entity[0] == ENTITY_TERM:
                    term = entity[1]
                    id_to_term[term.id] = term
                    name_to_id[term.name] = term.id
                curr_lines = []
                continue
            curr_lines.append(line)

        for term in id_to_term.values():
            for sup_term_id in [x for x in term.is_a]:
                id_to_term[sup_term_id].inv_is_a.add(term.id)
        
    return OntologyGraph(id_to_term, name_to_id)

def parse_entity(lines):
    if lines[0].strip() == "[Term]":
        attrs = {}
        for line in lines:
            tokens = line.split(":")
            if not tokens[0].strip() in attrs.keys():
                attrs[tokens[0].strip()] = []
            attrs[tokens[0].strip()].append(":".join(tokens[1:]).strip())
       
        definition = attrs["def"][0] if "def" in attrs.keys() else None
        synonyms = parse_synonyms(attrs["synonym"]) if "synonym" in attrs.keys() else Set()
        is_a = [x.split("!")[0].split()[0].strip() for x in attrs["is_a"]] if "is_a" in attrs.keys() else Set()

        return (ENTITY_TERM, Term(attrs["id"][0], attrs["name"][0].lower().strip(), definition, Set(synonyms), Set(is_a)))        

def parse_synonyms(raw_syns):
    synonyms = Set()
    for syn in raw_syns:
        m = re.search('\".+\"', syn)
        synonyms.add(m.group(0).lower()[1:-1])
    return [x.lower().strip() for x in synonyms]
    
if __name__ == "__main__":
    main()
        
