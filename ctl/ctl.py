from . import trees
import ply.yacc as yacc
import ply.lex as lex

tokens = [
        "IFF", "IMPLIES", "OPENPAREN", "CLOSEPAREN",
        "AND", "OR", "NOT", "TRUE", "FALSE", "PRED",
        "AX", "EX", "AF", "EF", "AG", "EG", "AU", "EU"
        ]

t_ignore = ' \t'
t_IFF = r'<->'
t_IMPLIES = r'->'
t_OPENPAREN = r'\('
t_CLOSEPAREN = r'\)'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_TRUE = r'true'
t_FALSE = r'false'
t_AX = r'AX'
t_EX = r'EX'
t_AF = r'AF'
t_EF = r'EF'
t_AG = r'AG'
t_EG = r'EG'
t_AU = r'AU'
t_EU = r'EU'
t_PRED = r'[a-z0-9_]+'
def t_error(te):
    print("Illegal character '{}'".format(te.value[0]))
    te.lexer.skip(1)

lexer = lex.lex()

def p_expr(p):
    '''expr : const
            | unary
            | binary
            | paren'''
    p[0] = p[1]

def p_const(p):
    '''const : TRUE 
             | FALSE 
             | PRED'''
    p[0] = trees.Tree(p[1], [])

def p_unary(p):
    '''unary : NOT expr
             | AX expr
             | EX expr
             | AG expr
             | EG expr
             | AF expr
             | EF expr'''
    p[0] = trees.Tree(p[1], [p[2]])

def p_binary(p):
    '''binary : expr IFF expr 
              | expr IMPLIES expr
              | expr AND expr
              | expr OR expr
              | expr AU expr
              | expr EU expr'''
    p[0] = trees.Tree(p[2], [p[1], p[3]])

def p_paren(p):
    '''paren : OPENPAREN expr CLOSEPAREN'''
    p[0] = p[2]

PARSER = yacc.yacc()

def parse(string):
    return PARSER.parse(string, lexer=lexer)

def node(v, c):
    return trees.Tree(v, c)

def simplify_tree(tree):
    case = tree.val
    children = [simplify_tree(c) for c in tree.children]
    if case == "AF":
        return node("!", node("EG", node("!", children[0])))
    elif case == "EF":
        return node("EU", [node("true", []), children[0]])
    elif case == "&&":
        return node("!", node("||", [node("!", children[0]), node("!", children[1])]))
    elif case == "AX":
        return node("!", node("EX", node("!", children[0])))
    elif case == "AG":
        return node("!", node("EU", [node("true", []), node("!", children[0])]))
    elif case == "AU":
        return node("!", node("||", [
            node("EU", [
                node("!", children[1]),
                node("!", node("||", children))]),
            node("EG", node("!", children[1]))]))
    elif case == "->":
        return node("||", [node("!", children[0]), children[1]])
    else:
        return node(case, children)
