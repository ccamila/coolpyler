import parser
from utils.errors import Error, Warning
from collections import defaultdict
from utils.ast_helper import type_fields
from copy import deepcopy

# Para facilitar a criação dos maps
Method = type_fields['Method']
Type = type_fields['Types']
Ident = type_fields['Ident']
Formal = type_fields['Formal']
Attr = type_fields['Attr']

class Semantic:
        def __init__(self, file):

            self.classes_map = {}
            self.method_map = {}

            self.ast = parser.get_ast(file)
            # graph with
            self.graph = defaultdict(set)


        ## ----------------------> PASSO (1)
        def map_and_create_initial_graph(self):

            '''
            The Object class is the root of the inheritance graph
                abort() : Object
                type_name() : String
                copy() : SELF_TYPE
            '''
            
            object = Type(name="Object", inherits=None,features=[
                Method(ident = Ident(name = 'abort'), type = 'Object', formals = (), expr = None),
                Method(ident = Ident(name = 'copy'), type = 'SELF_TYPE', formals = (), expr = None),
                Method(ident = Ident(name = 'type_name'), type = 'SELF_TYPE', formals = (), expr = None)
            ])

            '''
            The IO class provides the following methods for performing simple input and output operations
                out_string(x : String) : SELF_TYPE
                out_int(x : Int) : SELF_TYPE
                in_string() : String
                in_int() : Int
            '''
            
            input_output = Type(name="IO", inherits="Object",features=[
                Method(ident = Ident(name = 'input_integer'), type = 'SELF_TYPE', formals = (), expr = None),
                Method(ident = Ident(name = 'input_string'), type = 'SELF_TYPE', formals = (), expr = None),
                Method(ident = Ident(name = 'output_int'),type = 'SELF_TYPE',
                    formals = (
                        Formal(ident = Ident(name = 'arg'), type = 'Int'),
                    ),
                    expr = None
                ),
                Method(ident = Ident(name = 'out_string'),type = 'SELF_TYPE',
                    formals = (
                        Formal(Ident(name = 'arg'), type = 'String'),
                    ),
                    expr = None
                )
            ])

            '''
            The Int class provides integers. 
            There are no methods special to Int.
            '''

            integer = Type(name="Int", inherits="Object",features=[
                Attr(ident = Ident(name = '_val'), type = 'Int', expr = None)
            ])

            '''
            The Bool class provides true and false
            '''

            boolc = Type(name="Bool", inherits="Object",features=[
                Attr(ident = Ident(name = '_val'), type = 'Bool', expr = None)
            ])

            '''
            The String class provides strings. The following methods are defined
                length() : Int
                concat(s : String) : String
                substr(i : Int, l : Int) : String
            '''

            stringc = Type(name="String", inherits="Object",features=[
                Attr(ident = Ident(name = '_val'), type = 'Int', expr = None),
                Attr(ident = Ident(name = '_str_field'), type = 'SELF_TYPE', expr = None),
                Method(ident = Ident(name = 'length'), type = 'Int', formals = (), expr = None),
                Method(ident = Ident(name = 'concat'), type = 'String',
                    formals = (
                        Formal(Ident(name = 'arg'), type = 'Int'),
                    ),
                    expr = None
                ),
                Method(ident = Ident(name = 'substr'),type = 'String',
                    formals = (
                        Formal(ident = Ident(name = 'arg1'), type = 'Int'),
                        Formal(ident = Ident(name = 'arg2'), type = 'Int')
                    ),
                    expr = None
                )
            ])

            self.ast = (object, input_output, stringc, integer, boolc,) + self.ast
            
            '''
            A class may inherit only from a single class; this is aptly called 'single inheritance'
            The parent-child relation on classes defines a graph. This graph may not contain cycles.
            '''

            for cl in self.ast:
                if cl.name in self.classes_map:
                    raise Error("classe %s ja adicionada" % cl.name)
                self.classes_map[cl.name] = cl
                if cl.name == "Object":
                    # print('debug: desconsideramos o object')
                    continue 
                if cl.inherits:
                    self.graph[cl.inherits].add(cl.name)
                else:
                    self.graph["Object"].add(cl.name)


        ## ----------------------> PASSO (2)
        def check_for_wrong_inheritance(self):
            for parent in ['Int','String', 'Bool']:
                for name in self.graph[parent]:
                    raise Error("Classe tentando herdar de Int, String e Booleano")        


        ## ----------------------> PASSO (3)
        def check_for_undefined_classes(self):
            for _parent in list(self.graph.keys()):
                if _parent not in self.classes_map and _parent != "Object":
                    Warning('Classe sem pai ou indefinido. Realocando-o como um Object.')
                    # FROM COOL MANUAL
                    # There is a distinguished class Object. If a class definition does not specify a parent class, then the
                    # class inherits from Object by default. 
                    merge = self.graph['Object'] | self.graph[_parent]
                    self.graph['Object'] = merge
                    del self.graph[_parent]


        def create_method_map(self):
            '''
            An class cant have the same method declared multiple times
            '''
            checked_method = dict()
            for _class in self.ast:
                for feature in _class.features:
                    if isinstance(feature, Method):
                        tmp = (feature.ident.name, _class.name)
                        if tmp in checked_method:
                            raise Error("Metodo já definido")
                        checked_method[tmp] = feature.type
            self.method_map = checked_method


        def check_inheritance_tree(self,initial_class, checked):
            checked[initial_class] = True
            if initial_class not in self.graph.keys():
                return True

            for child in self.graph[initial_class]:
                self.check_inheritance_tree(child, checked)
            return True

        def check_for_inheritance_cycles(self):
            '''
            This graph may not contain cycles. 
            For example, if C inherits from P, then P must not inherit from C. Furthermore, if C inherits from
            P, then P must have a class definition somewhere in the program. Because Cool has single inheritance, it
            follows that if both of these restrictions are satisfied, then the inheritance graph forms a tree with Object
            as the root.
            '''
            checked = {}
            for parent in self.graph.keys():
                checked[parent] = False
                for cl_name in self.graph[parent]:
                    checked[cl_name] = False
            self.check_inheritance_tree("Object", checked)

            for _,value in checked.items():
                if not value:
                    raise Error("Herança Cíclica.")

        def infer_return_types(self,cl):
            # wip
            '''
            The Cool type system guarantees at compile time that execution of a program cannot result in runtime
            type errors. Using the type declarations for identifiers supplied by the programmer, the type checker
            infers a type for every expression in the program.
            '''
            return 0;

        def expand_inherited_classes(self, start_class="Object"):
            """
            Apply the following inheritance rules through the class graph:
                1- The Object class is the root of the inheritance graph.
                2- A class can make use of the methods in the IO class by inheriting from IO. It is an error to redefine the IO class
                3- It is an error to inherit from or redefine Int.
                4- It is an error to inherit from or redefine String.
                5- It is an error to inherit from or redefine Bool.
            """

            _class = self.classes_map[start_class]

            if _class.inherits:
                _class_parent = self.classes_map[_class.inherits]
                attr_set_child = [i for i in _class.features if isinstance(i, Attr)]
                attr_set_parent = [i for i in _class_parent.features if isinstance(i, Attr)]
                
                for attr in attr_set_child:
                    for p in attr_set_parent:
                        if attr.name == p.name:
                            raise Error("É um erro redefinir a classe")

                all_methods_from_child = [i for i in _class.features if isinstance(i, Method)]
                all_methods_from_parent = [i for i in _class_parent.features if isinstance(i, Method)]

                def header_method_classes(method_set):
                    all_methods = {}
                
                    for method in method_set:
                        all_methods[method.ident.name] = {}
                        for formal in method.formals:
                            all_methods[method.ident.name][formal.ident.name] = formal.type
                        all_methods[method.ident.name]['return'] = method.type
                
                    return all_methods

                methods_child = header_method_classes(all_methods_from_child)
                methods_parent = header_method_classes(all_methods_from_parent)

                methods_in_child = set()

                for method in all_methods_from_child:
                    methods_in_child.add(method.ident.name)
                    if method.ident.name in methods_parent:
                        parent_signature = methods_parent[method.ident.name]
                        child_signature = methods_child[method.ident.name]
                        if parent_signature != child_signature:
                            raise Error("Erro de redefinicao")

                for method in all_methods_from_parent:
                    if method.ident.name not in methods_in_child:
                        _class.features.append(deepcopy(method))
                for attr in attr_set_parent:
                    _class.features.append(deepcopy(attr))

            all_children = self.graph[start_class]
            for child in all_children:
                self.expand_inherited_classes(child)

        def is_child(self,child_class, parent_class):
            """check whether child class is a descendent of parent class"""
            if child_class == parent_class:
                return True
            for _class in self.graph[parent_class]:
                if self.is_child(child_class, _class):
                    return True
            return False

        def type_check(self,cl):
            # wip
            '''Make sure the inferred types match the declared types'''

def main(sourcefile):
    try:
        s = Semantic(sourcefile)

        # TODO: Fix type check on classes map
        # class_map_values = s.classes_map.values()
        # for classes in class_map_values:
            # s.type_check(classes)
        
        # TODO: Fix inference type function
        # s.infer_return_types(classes)

        s.map_and_create_initial_graph()
        s.check_for_wrong_inheritance()
        s.check_for_undefined_classes()        
        s.expand_inherited_classes()
        s.create_method_map()
        s.check_for_inheritance_cycles()

        print("\n\n\n SEMANTIC CHECK DONE \n\n\n")

        # TODO: Create an print function for best visualization
        # print(s.ast)
        return s.ast
    
    except Exception as e:
        print ("Error: %s"% e)
        
    """Recursive function to print the AST.
    
    Args:
        tree: An abstract syntax tree consisting of tuples, namedtuples and other objects.
        level: The indent level, used for the recursive calls.
        inline: Whether or not to indent the first line.
        
    Returns:
        Nothing. The AST is printed directly to stdout.
        
    """
if __name__ == '__main__':
    import sys
    sourcefile = sys.argv[1]
    main(sourcefile)