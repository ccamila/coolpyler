# =======
# HELP: https://gabrijel-boduljak.com/writing-a-compiler/
#       https://theory.stanford.edu/~aiken/software/cool/cool-manual.pdf
# =======
# Yacc example

import ply.yacc as yacc
import logging
log = logging.getLogger('ply')

# Get the token map from the lexer.  This is required.
import lexer
import ast

tokens = lexer.tokens

# The precedence of infix binary and prefix unary operations, from highest to lowest, is given by the
# following table:
# .
# @
# ~
# isvoid
# * /
# + -
# <= < =
# not
# <-
# All binary operations are left-associative, with the exception of assignment, which is right-associative,
# and the three comparison operations, which do not associate

precedence = (
    ('right', 'ASSIGN'),
    ('left', 'NOT'), # WIP: eh realmente left?
    ('nonassoc', 'LESS_THAN_OR_EQUAL', 'LESS_THAN', 'EQUAL' ),  # Nonassociative operators
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('left', 'ISVOID'), 
    ('left', 'INT_COMP'),
    ('left', 'AT'),
    ('left', 'DOT')  
)
def p_program(p):
    """program : classes"""
    p[0] = p[1]

def p_classes(p):
    """classes : class
               | class classes"""
    if len(p) == 2:
        p[0] = (p[1],)
    elif len(p) == 3:
        p[0] = (p[1],) + p[2]

def p_class(p):
    """class : CLASS TYPE inheritance BLOCK_INIT features_opt BLOCK_END SEMICOLON"""
    p[0] = ('class_type', 'name', p[2], 'inherits', p[3], 'features', p[5]) # ast.Type(name=p[2], inherits=p[3], features=p[5])

def p_inheritance(p):
    """inheritance : INHERITS TYPE
                   | empty"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[2]
    else:
        raise SyntaxError('Invalid number of symbols')

def p_features_opt(p):
    """features_opt : features
                    | empty"""
    if p.slice[1].type == 'empty':
        p[0] = tuple()
    else:
        p[0] = p[1]

def p_features(p):
    """features : feature
                | feature features"""
    if len(p) == 2:
        p[0] = (p[1],)
    elif len(p) == 3:
        p[0] = (p[1],) + p[2]
    else:
        raise SyntaxError('Invalid number of symbols')

def p_feature(p):
    """feature : ID PARENTESIS_INIT formals_opt PARENTESIS_END COLON TYPE '{' expr '}' SEMICOLON
               | attr_def SEMICOLON"""
    if len(p) == 11:
        p[0] = ('method', ('ident', p[1]), 'type', p[6], 'formals', p[3], 'expr', p[8]) # ast.Method(ident=ast.Ident(p[1]), type=p[6], formals=p[3], expr=p[8])
    elif len(p) == 3:
        p[0] = p[1]
    else:
        raise SyntaxError('Invalid number of symbols')

def p_attr_defs(p):
    """attr_defs : attr_def
                 | attr_def COMMA attr_defs"""
    if len(p) == 2:
        p[0] = (p[1],)
    elif len(p) == 4:
        p[0] = (p[1],) + p[3]
    else:
        raise SyntaxError('Invalid number of symbols')

def p_attr_def(p):
    """attr_def : ID COLON TYPE assign_opt"""
    p[0] = ('attribute', ('ident', p[1]), 'type', p[3], 'expr', p[4]) # ast.Attribute(ident=ast.Ident(p[1]), type=p[3], expr=p[4])

def p_assign_opt(p):
    """assign_opt : assign
                  | empty"""
    p[0] = p[1]

def p_assign(p):
    """assign : ASSIGN expr"""
    p[0] = p[2]

def p_formals_opt(p):
    """formals_opt : formals
                   | empty"""
    if p.slice[1].type == 'empty':
        p[0] = tuple()
    else:
        p[0] = p[1]

def p_formals(p):
    """formals : formal
               | formal COMMA formals"""
    if len(p) == 2:
        p[0] = (p[1],)
    elif len(p) == 4:
        p[0] = (p[1],) + p[3]
    else:
        raise SyntaxError('Invalid number of symbols')

def p_formal(p):
    """formal : ID COLON TYPE"""
    p[0] =  ('formal', ('ident', p[1]), 'type', p[3]) #ast.Formal(ident=ast.Ident(p[1]), type=p[3])

def p_params_opt(p):
    """params_opt : params
                  | empty"""
    if p.slice[1].type == 'empty':
        p[0] = tuple()
    else:
        p[0] = p[1]

def p_params(p):
    """params : expr
              | expr COMMA params"""
    if len(p) == 2:
        p[0] = (p[1],)
    elif len(p) == 4:
        p[0] = (p[1],) + p[3]

def p_block(p):
    """block : blockelements"""
    p[0] = ast.Block(p[1])

def p_blockelements(p):
    """blockelements : expr SEMICOLON
                     | expr SEMICOLON blockelements"""
    if len(p) == 3:
        p[0] = (p[1],)
    elif len(p) == 4:
        p[0] = (p[1],) + p[3]


def p_function_call(p):
    """function_call : ID PARENTESIS_INIT params_opt PARENTESIS_END"""
    p[0] = ('function_call', ('ident', p[1]), 'params', p[3]) # ast.FunctionCall(ident=ast.Ident(p[1]), params=p[3])

def p_targettype_opt(p):
    """targettype_opt : targettype
                      | empty"""
    p[0] = p[1]

def p_targettype(p):
    """targettype : AT TYPE"""
    p[0] = p[2]
    
def p_expr(p):
    """expr : ID assign
            | expr targettype_opt DOT function_call
            | function_call
            | IF expr THEN expr ELSE expr FI
            | WHILE expr LOOP expr POOL
            | LET attr_defs IN expr
            | CASE expr OF typeactions ESAC
            | NEW TYPE
            | INT_COMP expr
            | NOT expr
            | ISVOID expr
            | expr PLUS expr
            | expr MINUS expr
            | expr MULTIPLY expr
            | expr DIVIDE expr
            | expr LESS_THAN expr
            | expr LESS_THAN_OR_EQUAL expr
            | expr EQUAL expr
            | BLOCK_INIT block BLOCK_END
            | PARENTESIS_INIT expr PARENTESIS_END
            | ID
            | INTEGER
            | STRING
    """
    first_token = p.slice[1].type
    second_token = p.slice[2].type if len(p) > 2 else None
    third_token = p.slice[3].type if len(p) > 3 else None

    if first_token == 'ID':

        if second_token is None:
            p[0] = ('assign', p[1])
        
        elif second_token == 'assign':
            p[0] = ('first-token', ('assign', p[1]), p[2])

    elif first_token == 'expr':
        
        if len(p) == 4 and third_token == 'expr':
            p[0] = ('first-token', p[2], p[1], p[3])
        
        elif third_token == 'DOT':
            p[0] = ('first-token', p[1], p[2], p[4])

    elif first_token == 'function_call':
        p[0] = p[1]

    elif first_token == 'IF':
        p[0] = ('first-token', p[2], p[4], p[6])
    
    elif first_token == 'WHILE':
        p[0] = ('first-token', p[2], p[4])
    
    elif first_token == 'LET':
        p[0] = ('first-token', p[2], p[4])
    
    elif first_token == 'CASE':
        p[0] = ('first-token', p[2], p[4])
    
    elif first_token == 'NEW':
        p[0] = ('first-token', p[2])
    
    elif first_token in ['ISVOID', 'INT_COMP', 'NOT']:
        p[0] = ('first-token', p[1], p[2])
    
    elif first_token in ['LBRACE', 'LPAREN']:
        p[0] = p[2]
    
    elif first_token in ['INTEGER', 'STRING']:
        p[0] = p[1]

def p_empty(p):
    """empty :"""
    p[0] = None

def p_error(p):
    print("Syntax error in input!")
# Create parser
parser = yacc.yacc()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        data = open(sys.argv[1], 'r').read()
        result = yacc.parse(data)
        print(result)
    else:
        while True:
            try:
                s = input('coolp> ')
            except EOFError:
                break
            if not s: continue
            result = yacc.parse(s)
            print(result)

