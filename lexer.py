# =========================
# PLY (Python Lex-Yacc): https://github.com/dabeaz/ply 
# =========================

from distutils.debug import DEBUG
import ply.lex as lex
from ply.yacc import yacc

# --- Tokenizer

# All tokens must be named in advance.

# D E F I N I T I O N S =========================

# Reserved keywords

reserved_keywords = {
            "case": "CASE",
            "class": "CLASS",
            "else": "ELSE",
            "esac": "ESAC",
            "fi": "FI",
            "if": "IF",
            "in": "IN",
            "inherits": "INHERITS",
            "isvoid": "ISVOID",
            "let": "LET",
            "loop": "LOOP",
            "new": "NEW",
            "of": "OF",
            "pool": "POOL",
            "self": "SELF",
            "then": "THEN",
            "while": "WHILE"
        }

reserved_keywords_values = reserved_keywords.values()

tokens = ( 
    'ASSIGN', 'BOOL','NOT', 'EQUAL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'INT_COMP',
    'AT', 'DOT', 'ACTION',
    'BLOCK_INIT', 'BLOCK_END', 'PARENTESIS_INIT', 'PARENTESIS_END',
    'COLON', 'COMMA', 'SEMICOLON',
    'ID', 'TYPE',
    'INTEGER', 'STRING',
)+ tuple(reserved_keywords_values)



# R U L E S ========================= 

 # A regular expression rule with some action code

def t_INTEGER(t):
    r'[0-9]+'
    t.value = int(t.value)    
    return t

def t_BOOL(t):
    r'true|false'
    t.value = True if t.value == 'true' else False
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

def t_SINGLECOMMENT(t):
	r"\-\-[^\n]*"
	pass

def t_NOT(t):
    r'[nN][oO][tT]'
    return t

def t_TYPE(t):
    r'[A-Z][A-Za-z0-9_]*'
    return t

def t_ID(t):
    r'[a-z][A-Za-z0-9_]*'
    lower_type = t.value.lower();
    default = 'ID'
    t.type = reserved_keywords.get(lower_type, default)
    return t

def t_COMMENT(t):
  #r'(?:\(\*(?:(?!\*\))(.|\n|\r\n))*\*\))'
  r'\(\*'
  t.lexer.code_start = t.lexer.lexpos
  t.lexer.comment_count = 1
  t.lexer.begin('COMMENT')

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Error handling rule


def t_error(t):
    print("Illegal character '{}'" % t.value[0])
    t.lexer.skip(1)

t_ignore  = ' \t' + ' ' + '\n'

t_ACTION = r'\=\>' 
t_AT = r'\@'
t_BLOCK_INIT = r'\{' 
t_BLOCK_END = r'\}'
t_PARENTESIS_INIT = r'\('
t_PARENTESIS_END = r'\)'
t_COLON= r'\:'
t_COMMA=r'\,'
t_DOT=r'\.'
t_SEMICOLON=r'\;'

t_MINUS = r'\-'         
t_MULTIPLY = r'\*'      
t_PLUS = r'\+'
t_DIVIDE = r'\/'
t_EQUAL = r'\=' 
t_LESS_THAN = r'\<'            
t_LESS_THAN_OR_EQUAL = r'\<\='  
t_ASSIGN = r'\<\-'
t_INT_COMP = r'\~'


# L E X E R ========================= 

lexer = lex.lex()

# data = '''
# class Main inherits IO {
#    main(): SELF_TYPE {
# 	out_string("Hello, World.")
#    };
# };
# '''

# lexer.input(data)

# # Build the lexer object
# lex.lex()

###### PROCESS INPUT ######


if __name__ == '__main__':

    import sys
    sourcefile = sys.argv[1]

    with open(sourcefile, 'r') as source:
        lex.input(source.read())

    # Read tokens
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: 
            break      
        print(tok)

