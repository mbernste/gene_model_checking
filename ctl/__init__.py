from .ctl import parse, simplify_tree
from .checker import Model, check_formula

def check(model, formula):
    expr = simplify_tree(parse(formula))
    print expr
    labels = check_formula(model, expr) 
    print labels
    return expr in labels[model.start]

if __name__ == "__main__":
    print("Don't run this, silly")
