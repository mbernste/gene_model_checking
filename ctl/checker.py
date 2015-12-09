from collections import Counter
from .ctl import parse

class Model(object):
    def __init__(self):
        self.nodes = []
        self.edges = {}
        self.label = {}
    def submodel(self, nodes):
        edges = {n : self.edges[n] for n in nodes}
        label = {n : self.label[n] for n in nodes}
        m = Model()
        m.nodes, m.edges, m.label = nodes, edges, label
        return m
    def in_neighbors(self, node):
        result = set()
        for n in self.nodes:
            if node in self.edges[n]:
                result.add(n)
        return result
    def out_neighbors(self, node):
        return self.edges[node]
    def scc(self):
        # set up data structs
        visited, assigned = set(), set()
        L = []
        partition, current = {}, 0
        # recursive 'visit' for Kosaraju's
        def visit(n):
            if n not in visited:
                visited.add(n)
                for s in self.out_neighbors(n):
                    visit(s)
                L.append(n)
        # recursive 'assign'
        def assign(u, r):
            if n not in assigned:
                # add to appropriate partition
                try:
                    c = partition[r]
                except KeyError:
                    c = current
                    current += 1
                partition[u] = c
                assigned.add(u)
                # recurse
                for s in self.in_neighbors(n):
                    assign(s, r)
        for n in self.nodes:
            visit(n)
        for n in L:
            assign(n, n)
        # result is dict {n : c}
        return partition

def check_formula(model, start, formula):
    # we iterate bottom-up over all sub-formulas
    # -- the leaves must be predicates we can check with the model
    # -- everything else is in the form of the few ops we care about
    # -- the end result is a labeling of all model states s.t.
    # -- -- the starting state might be labeled with the 
    TRUE = parse("true")
    labels = {n : set([TRUE]) for n in model.nodes}
    for term in formula.subtrees():
        # case for ap (also captures 'true')
        if term.arity == 0 and term.val != 'false':
            for n in model.nodes:
                if term.val in model.label[n]:
                    labels[n].add(term)
        # case for negation
        elif term.arity == 1 and term.val == "!":
            for n in model.nodes:
                if term.children[0] not in labels[n]:
                    labels[n].add(term)
        # case for OR
        elif term.arity == 2 and term.val == "||":
            l, r = term.children
            for n in model.nodes:
                if l in labels[n] or r in labels[n]:
                    labels[n].add(term)
        # case for EX
        elif term.arity == 1 and term.val == "EX":
            f = term.children[0]
            for n in model.nodes:
                if any([f in labels[s] for s in model.out_neighbors(n)]):
                    labels[n].add(term)
        # case for EU
        elif term.arity == 2 and term.val == "EU":
            l, r = term.children
            worklist = []
            visited = set()
            # find starting points for backwards search
            for n in model.nodes:
                if r in labels[n]:
                    worklist.append(n)
            # go through worklist, adding labels
            while len(worklist) > 0:
                n = worklist.pop()
                if n not in visited:
                    # we haven't visited, so add
                    visited.add(n)
                    # we either started here, or
                    # we got added after l in labels check
                    # so state is labeled with EU(l, r)
                    labels[n].add(term)
                    for p in model.in_neighbors(n):
                        if l in labels[p]:
                            worklist.append(p)
        # case for EG
        elif term.arity == 1 and term.val == "EG":
            f = term.children[0]
            # first step - extract all values in a non-trivial SCC
            # get submodel from nodes w/f
            m = model.submodel([n for n in model.nodes if f in labels[n]])
            # get scc - filter by non-trivial
            partition = m.scc()
            counts = Counter(partition.values())
            # join all nodes in prev to worklist
            worklist = [n for n, c in partition.items() if counts[c] != 1]
            visited = set()
            while len(worklist) > 0:
                n = worklist.pop()
                if n not in visited:
                    visited.add(n)
                    labels[n].add(term)
                    for s in model.in_neighbors(n):
                        if f in labels[s]:
                            worklist.append(s)
    return formula in labels[start]
