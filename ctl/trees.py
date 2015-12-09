class Tree(object):
    def __init__(self, val, children):
        self.val = val
        if isinstance(children, list):
            self.children = children
        else:
            self.children = [children]
        self.arity = len(self.children)
    def positions(self):
        start = [[]]
        for i, c in enumerate(self.children):
            for p in c.positions():
                start.append( [i] + p )
        return start
    def at_position(self, pos):
        answer = self
        for p in pos:
            answer = answer.children[p]
        return answer
    def __repr__(self):
        kids = ",".join(repr(c) for c in self.children)
        return repr(self.val) + "(" + kids + ")"
    def linearize(self):
        start = [self.val]
        for c in self.children:
            start += c.linearize()
        return start
    def size(self):
        return len(self.linearize())
    def subtrees(self):
        return sorted([self.at_position(p) for p in self.positions()], key=lambda c: c.size())
    def __eq__(self, other):
        if not isinstance(other, Tree):
            return False
        if len(other.children) != len(self.children):
            return False
        if other.val != self.val:
            return False
        else:
            return all([l == r for l, r in zip(self.children, other.children)])
    def __hash__(self):
        return hash(repr(self))

if __name__ == "__main__":
    test = Tree("+", [Tree(1, [Tree("Ha", [])]), Tree(2, [])])
    for p in test.positions():
        print(p, test.at_position(p))
    print(test.subtrees())
