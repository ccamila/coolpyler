# =======
# HELP: https://gabrijel-boduljak.com/writing-a-compiler/
#       https://theory.stanford.edu/~aiken/software/cool/cool-manual.pdf
# =======

import ply.yacc as yacc
# Get the token map from the lexer.  This is required.
import lexer
import utils.ast_helper as ast

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
    ('left', 'NOT'),
    ('nonassoc', 'EQUAL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
    ('right', 'ISVOID'),
    ('right', 'INT_COMP'),
    ('left', 'AT'),
    ('left', 'DOT'),
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
    else:
        raise SyntaxError()

def p_class(p):
    """class : CLASS TYPE inheritance BLOCK_INIT features_opt BLOCK_END SEMICOLON"""
    p[0] = ast.type_fields['Types'](name=p[2], inherits=p[3], features=p[5])


def p_inheritance(p):
    """inheritance : INHERITS TYPE
                   | empty"""

    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[2]
    else:
        raise SyntaxError()

def p_features_opt(p):
    """features_opt : features
                    | empty"""
    if p.slice[1].type == 'empty':
        p[0] = []
    else:
        p[0] = p[1]

def p_features(p):
    """features : feature
                | feature features"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        raise SyntaxError()

def p_feature(p):
    """feature : ID PARENTESIS_INIT formals_opt PARENTESIS_END COLON TYPE BLOCK_INIT expr BLOCK_END SEMICOLON
               | attr_def SEMICOLON"""
    if len(p) == 11:
        p[0] = ast.type_fields['Method'](ident=ast.type_fields['Ident'](p[1]), type=p[6], formals=p[3], expr=p[8])
    elif len(p) == 3:
        p[0] = p[1]
    else:
        raise SyntaxError()

def p_attr_defs(p):
    """attr_defs : attr_def
                 | attr_def COMMA attr_defs"""
    if len(p) == 2:
        p[0] = (p[1],)
    elif len(p) == 4:
        p[0] = (p[1],) + p[3]
    else:
        raise SyntaxError()

def p_attr_def(p):
    """attr_def : ID COLON TYPE assign_opt"""
    p[0] = ast.type_fields['Attr'](ident=ast.type_fields['Ident'](p[1]), type=p[3], expr=p[4])

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
        raise SyntaxError()

def p_formal(p):
    """formal : ID COLON TYPE"""
    p[0] = ast.type_fields['Formal'](ident=ast.type_fields['Ident'](p[1]), type=p[3])

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
    else:
        raise SyntaxError()

def p_block(p):
    """block : blockelements"""
    p[0] = ast.type_fields['Block'](p[1])

def p_blockelements(p):
    """blockelements : expr SEMICOLON
                     | expr SEMICOLON blockelements"""
    if len(p) == 3:
        p[0] = (p[1],)
    elif len(p) == 4:
        p[0] = (p[1],) + p[3]
    else:
        raise SyntaxError()

def p_typeactions(p):
    """typeactions : typeaction
                   | typeaction typeactions"""
    if len(p) == 2:
        p[0] = (p[1],)
    elif len(p) == 3:
        p[0] = (p[1],) + p[2]
    else:
        raise SyntaxError()

def p_typeaction(p):
    """typeaction : ID COLON TYPE ACTION expr SEMICOLON"""
    p[0] = ast.type_fields['TypeAction'](ident=ast.type_fields['Ident'](p[1]), type=p[3], expr=p[5])

def p_function_call(p):
    """function_call : ID PARENTESIS_INIT params_opt PARENTESIS_END"""
    p[0] = ast.type_fields['FunctCall'](ident=ast.type_fields['Ident'](p[1]), params=p[3])


def p_targettype_opt(p):
    """targettype_opt : targettype
                      | empty"""
    p[0] = p[1]

def p_targettype(p):
    """targettype : AT TYPE"""
    p[0] = p[2]

def p_expr_self(p):
    """expr  : SELF"""
    p[0] = ast.type_fields['Self'](ident=ast.type_fields['Ident'](p[1]))

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
            | BOOL
    """

    first_token = p.slice[1].type
    second_token = p.slice[2].type if len(p) > 2 else None
    third_token = p.slice[3].type if len(p) > 3 else None

    if first_token == 'ID':
        if second_token is None:
            p[0] = ast.type_fields['Ident'](p[1])
        elif second_token == 'assign':
            p[0] = ast.type_fields['Assign'](ident=ast.type_fields['Ident'](p[1]), expr=p[2])
    elif first_token == 'expr':
        if len(p) == 4 and third_token == 'expr':
            p[0] = ast.type_fields['BinOp'](operator=p[2], left=p[1], right=p[3])
        elif third_token == 'DOT':
            p[0] = ast.type_fields['MethodCall'](object=p[1], targettype=p[2], method=p[4])
    elif first_token == 'function_call':
        p[0] = p[1]
    elif first_token == 'IF':
        p[0] = ast.type_fields['If'](condition=p[2], true=p[4], false=p[6])
    elif first_token == 'WHILE':
        p[0] = ast.type_fields['While'](condition=p[2], action=p[4])
    elif first_token == 'LET':
        p[0] = ast.type_fields['Let'](assignments=p[2], expr=p[4])
    elif first_token == 'CASE':
        p[0] = ast.type_fields['Case'](expr=p[2], typeactions=p[4])
    elif first_token == 'NEW':
        p[0] = ast.type_fields['New'](p[2])
    elif first_token in ['ISVOID', 'INT_COMP', 'NOT']:
        p[0] = ast.type_fields['UnOp'](operator=p[1], right=p[2])
    elif first_token in ['BLOCK_INIT', 'PARENTESIS_INIT']:
        p[0] = p[2]
    elif first_token in ['INTEGER', 'STRING', 'BOOL']:
        p[0] = p[1]

def p_empty(p):
    """empty :"""
    p[0] = None

def p_error(p):
    print('Syntax error in input at {!r}'.format(p))

# Create parser
yacc.yacc()

def get_ast(sourcefile):
	with open(sourcefile, 'r') as source:
		t = yacc.parse(source.read())
	return t

if __name__ == '__main__':

    import sys
    from pprint import pprint

    # Get file as argument

    if len(sys.argv) != 2:
        print('You need to specify a cool source file to read from.', file=sys.stderr)
        sys.exit(1)
    if not sys.argv[1].endswith('.cl'):
        print('Argument needs to be a cool source file ending on ".cl".', file=sys.stderr)
        sys.exit(1)

    sourcefile = sys.argv[1]

    # Read and parse source file

    with open(sourcefile, 'r') as source:
        t = yacc.parse(source.read())

    print (t)
