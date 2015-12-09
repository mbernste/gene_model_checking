from .ctl import parse, simplify_tree
from .checker import Model, check_formula

def check(model, formula):
    expr = simplify_tree(parse(formula))
    return check_formula(model, model.nodes[0], expr) 

if __name__ == "__main__":
    print("Don't run this, silly")
