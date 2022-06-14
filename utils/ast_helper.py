import collections
import types

# A minimal way to construct a tree is to simply create 
# and propagate a tuple or list in each grammar rule function. 

#  class BinOp(Expr):
#      def __init__(self,left,op,right):
#          self.type = "binop"
#          self.left = left
#          self.right = right
#          self.op = op
 
#  class Number(Expr):
#      def __init__(self,value):
#          self.type = "number"
#          self.value = value
 

class Returnable:
    return_type = None    

def named_tuple(type_name, fields):
    return types.new_class(type_name, (Returnable, collections.namedtuple(type_name, fields)))

type_fields = {
'Assign' : named_tuple('Assign', 'ident expr'),
'Attr': named_tuple('Attribute', 'ident type expr'),
'BinOp': named_tuple('BinaryOperation', 'operator left right'),
'Block': named_tuple('Block', 'elements'),
'Case': named_tuple('Case', 'expr typeactions'),
'Formal': named_tuple('Formal', 'ident type'),
'FunctCall': named_tuple('FunctionCall', 'ident params'),
'Ident': named_tuple('Ident', 'name'),
'If': named_tuple('If', 'condition true false'),
'Let': named_tuple('Let', 'assignments expr'),
'Method': named_tuple('Method', 'ident type formals expr'),
'MethodCall': named_tuple('MethodCall', 'object targettype method'),
'New': named_tuple('New', 'type'),
'Self': named_tuple('Self','ident'),
'Types': named_tuple('Type', 'name inherits features'),
'TypeAction': named_tuple('TypeAction', 'ident type expr'),
'UnOp': named_tuple('UnaryOperation', 'operator right'),
'While': named_tuple('While', 'condition action'),
}
