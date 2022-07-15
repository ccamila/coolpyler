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
BinOp = type_fields['BinOp']
While = type_fields['While']

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

            # print(self.ast)

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
            
            '''
            The Cool type system guarantees at compile time that execution of a program cannot result in runtime
            type errors. Using the type declarations for identifiers supplied by the programmer, the type checker
            infers a type for every expression in the program.
            '''
            variable_scopes  = [dict()]
            seen_attribute = set()
            seen_method = set()
            
            # Checa os atributos para evitar repeticao
            for feature in cl.features:

                if isinstance(feature, Attr):
                    if feature.ident.name in seen_attribute:
                        raise Error("Atributo %s ja esta definido." %feature.ident.name)

                    seen_attribute.add(feature.ident.name)

                    if feature.type == "SELF_TYPE":
                        variable_scopes[-1][feature.ident.name] = cl.name
                    else:
                        variable_scopes[-1][feature.ident.name] = feature.type #[-1] is for latest scope

            # Checa os metodos para evitar repeticao
            for feature in cl.features:

                if isinstance(feature, Method):
                    if feature.ident.name in seen_method:
                        raise Error("Metodo %s ja esta definido." %feature.name)

                    seen_method.add(feature.ident.name)
                    variable_scopes.append(dict()) #adding new scope

                    seen_formals = set()

                    # Checa as variaveis locais para evitar repeticao
                    for form in feature.formals:

                        if form.ident.name in seen_formals:
                            raise Error("A Variavel %s no metodo %s ja esta definida." %(form.ident.name, feature.name))

                        seen_formals.add(form)
                        variable_scopes[-1][form.ident.name] = form.type
                    
                    self.traverse_expression(feature.expr, variable_scopes, cl)
                    del variable_scopes[-1]
                
                elif isinstance(feature, Attr):
                    self.traverse_expression(feature.expr, variable_scopes, cl)


        def traverse_expression(self, expression, variable_scopes, cl):

            if isinstance(expression, BinOp):
                self.traverse_expression(expression.left, variable_scopes, cl)
                self.traverse_expression(expression.right, variable_scopes, cl)
                if expression.operator in ['<', '>', '==']:
                    expression.return_type = 'Bool'
                else:
                    expression.return_type = 'Int'
                

            elif isinstance(expression, While):
                self.traverse_expression(expression.condition, variable_scopes, cl)
                self.traverse_expression(expression.action, variable_scopes, cl)
                

            elif isinstance(expression, type_fields['Block']):
                last_type = None
                for expr in expression.elements:
                    self.traverse_expression(expr, variable_scopes, cl)
                    last_type = getattr(expr, 'return_type', None)
                expression.return_type = last_type
                

            elif isinstance(expression, type_fields['Assign']):
                self.traverse_expression(expression.expr, variable_scopes, cl)
                self.traverse_expression(expression.ident, variable_scopes, cl)
                expression.return_type = expression.ident.return_type
                

            elif isinstance(expression, type_fields['If']):
                self.traverse_expression(expression.condition, variable_scopes, cl)
                self.traverse_expression(expression.true, variable_scopes, cl)
                self.traverse_expression(expression.false, variable_scopes, cl)
                
                true_type = self.classes_map[expression.true.return_type]
                false_tyep = self.classes_map[expression.false.return_type]

            elif isinstance(expression, type_fields['Case']):
                pass

            elif isinstance(expression, type_fields['New']):
                if expression.type == 'SELF_TYPE':
                    expression.return_type = cl.name
                    return

                expression.return_type = expression.type
                
            elif isinstance(expression, Ident):
                for scope in variable_scopes[::-1]:
                    if expression.name in scope:
                        expression.return_type = scope[expression.name]
                        return
                        
                raise Error("Variavel local nao declarada no escopo: " + expression.name + " na classe: " + cl.name)

            elif isinstance(expression, type_fields['Assign']):
                tmp = (expression.ident.name, cl.name)
                
                if  tmp not in self.method_map:
                    raise Error("Funcao nao definida no escopo: " + expression.ident.name + " na classe: " + cl.name)
                else:
                    if self.method_map[tmp] == 'SELF_TYPE':
                        pass
                    else:
                        expression.return_type = self.method_map[tmp]
            

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
            '''Make sure the inferred types match the declared types'''
            for feature in cl.features:
                if isinstance(feature, Attr):
                    
                    if feature.type == "SELF_TYPE":
                        realtype = cl.name
                    else:
                        realtype = feature.type
                    if feature.expr:
                        self.check_expression_type(feature.expr,cl)
                        child_type = feature.expr.return_type
                        parent_type = realtype
                        if not self.is_child(child_type,parent_type):
                            raise Error("Tipo inferido %s para o atributo %s diferente do declado %s" % (child_type, feature.ident.name, parent_type))
                elif isinstance(feature, Method):
                    for formal in feature.formals:
                        if formal.type == "SELF_TYPE":
                            raise Error("%s não pode ter self type" % formal[0])
                        elif formal.type not in self.classes_map:
                            raise Error("%s tipo indefinido" % formal.ident.name)

                        if feature.type == "SELF_TYPE":
                            real_return_type = cl.name
                        else:
                            real_return_type = feature.type

                        if feature.expr is None:
                            if feature.type == "SELF_TYPE":
                                returned_type = cl.name
                            else:
                                returned_type = feature.type

                        else:
                            self.check_expression_type(feature.expr,cl)
                            returned_type = feature.type
                        if not self.is_child(returned_type,real_return_type):
                            raise Error("tipo inferido %s no metodo %s nao esta conforme o tipo declarado %s") %(returned_type,feature.ident.name,real_return_type)

        def check_expression_type(self,expression,cl):
            '''make sure types validate at any point in the ast'''
            #print(expression)
            if isinstance(expression, type_fields['Assign']):
                self.check_expression_type(expression.expr, cl)
                if not self.is_child(expression.expr.return_type, expression.ident.name.return_type):
                    raise Error("Tipo inferido %s em %s nao estah conforme o tipo declarado %s" % (expression.expr.return_type, expression.ident.name, expression.name.return_type))
            
            elif isinstance(expression, BinOp):
                self.check_expression_type(expression.left,cl)
                self.check_expression_type(expression.right,cl)
                if not (self.is_child(expression.left.return_type, expression.right.return_type) or self.is_child(expression.right.return_type, expression.left.return_type)):
                    raise Error("Tipo inferido %s em %s nao estah conforme o tipo declarado %s em %s" % (expression.left.return_type, expression.operator, expression.right.return_type, expression))

            elif isinstance(expression, type_fields['If']):
                self.check_expression_type(expression.condition, cl)
                self.check_expression_type(expression.true, cl)
                self.check_expression_type(expression.false, cl)
                if expression.condition.return_type != "Bool":
                    raise Error("Condicionais do tipo IF devem ter condições booleanas declaradas")

            elif isinstance(expression, type_fields['Let']):
                for line in expression.elements:
                    self.check_expression_type(line,cl)

            elif isinstance(expression, type_fields['While']):
                self.check_expression_type(expression.condition,cl)
                self.check_expression_type(expression.body, cl)
                if expression.condition.return_type != "Bool":
                        raise Error("Condicionais do tipo WHILE devem ter condições booleanas declaradas") 

def main(sourcefile):
    try:
        s = Semantic(sourcefile)

        s.map_and_create_initial_graph()
        s.check_for_wrong_inheritance()
        s.check_for_undefined_classes()        
        s.expand_inherited_classes()
        s.create_method_map()
        s.check_for_inheritance_cycles()

        class_map_values = s.classes_map.values()

        # print(class_map_values)

        for classes in class_map_values:
            s.infer_return_types(classes)

        for classes in class_map_values:
            s.type_check(classes)

        print("\n\n\n SEMANTIC CHECK DONE \n\n\n")

        # TODO: Create an print function for best visualization
        # print(s.ast)
        return s.ast
    
    except Exception as e:
        print ("Error: %s"% e)

if __name__ == '__main__':
    import sys
    sourcefile = sys.argv[1]
    main(sourcefile)