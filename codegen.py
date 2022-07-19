from semantic import main
from utils.errors import Error, Warning
from utils.ast_helper import type_fields

Method = type_fields['Method']
Type = type_fields['Types']
Ident = type_fields['Ident']
Formal = type_fields['Formal']
Attr = type_fields['Attr']
BinOp = type_fields['BinOp']
While = type_fields['While']

inbuilt_functions = {
    "input_integer" :   "",
    "input_string" :   "",
    "output_int" :   "",
    "out_string" :   "",
    "abort" :   "",
    "copy" :   "",
    "type_name" :   ""
}

def io_out_string(arg):
    pass

class CodeGen:

    def __init__(self, sourcefile):
        self.ast = main(sourcefile)
        # print('RESULTADO DA FASE SEMANTICA:')
        # print(self.ast)
        # print('-----------------------------')
        self.out_file = sourcefile + ".bril"

    def write(self, s, n=0):
        line = ""
        line += "\t"*n
        line += s 
        line += "\n"
        with open(self.out_file, "a") as f:
            f.write(line)
        
    
    def check_for_Main_class(self):
        self.write("@main {", 0)
        main_class = ()
        for cl in self.ast:
            if cl.name == "Main":
                # Define quem é a main class.
                self.main_class = cl
                main_class = cl
                break

        main_class_not_finded = main_class

        if main_class_not_finded == ():
            raise Error("Não existe classe main. O programa é inválido")   

        for feature in main_class.features:
            
            # Checa declaração de variaveis globais
            if isinstance(feature, type_fields['Attr']):

                # print("FEATURE ----------------")
                # print(feature)
                # print("END FEATURE ----------------\n")

                data_type = ""
                value = ""
                findedAttr = False
                if feature.type == "Int":
                    data_type = "int"
                    value  = "0"
                    findedAttr = True

                if feature.type == "Bool":
                    data_type = "bool"
                    value  = "False"
                    findedAttr = True
                
                # O  tipo string não é suportado em birl
                elif feature.type == "String":
                    print('STRING: Não eh reconhecido.')
                
                if findedAttr:
                    # Se acha, grava no arquivo.
                    s = feature.ident.name + ": " + data_type + " = const " + value
                    self.write(s, 1)
                

    def add_basic_operation(self,stmt):
        # print("add_binary_operation STMT ----------------")
        # print(stmt.operator)
        # print("END MAIN----------------\n")
        # Qual variavel colocar?         
        if stmt.operator == '+':
            print('add ' + str(stmt.left.name)+ " " + str(stmt.right.name))
        if stmt.operator == '-':
            print('sub ' + str(stmt.left.name)+ " " + str(stmt.right.name))
        if stmt.operator == '/':
            print('div ' + str(stmt.left.name)+ " " + str(stmt.right.name))
        if stmt.operator == '*':
            print('mul ' + str(stmt.left.name)+ " " + str(stmt.right.name))        
    
    def add_left_value(self,stmt):
        pass

    def add_statement(self,stmt):
        print("add_statement stmt ----------------")
        print(stmt)
        print("END ----------------\n")
        if isinstance(stmt,type_fields['Assign']):
            self.add_statement(stmt.expr)
            self.add_left_value(stmt.ident)
        if isinstance(stmt,type_fields['BinOp']):
            self.add_basic_operation(stmt)
        if isinstance(stmt, type_fields['FunctCall']):
            # Se é uma função, precisamos reconhecer seus parametros.
            self.add_params(stmt.params) 
        if isinstance(stmt, int):
            # caso seja inteiro.
            print()

    def add_params(self, params):
        for i in params:
            # print('FunctionCall add_params i')
            # print(i)
            # print('Call add_statement again >>')
            self.add_statement(i)

    def add_function(self, method, cl):
        """ Adding Function """
        print("method ----------------")
        print(method)
        print("END ----------------\n")
        for i in method.expr:
            for innerElement in i:
                self.add_statement(innerElement)

    def analyzer_functions(self):
        """ Adding all functions other than Main """
        # print("self.main_class.features ----------------")
        # print(self.main_class.features)
        # print("END ----------------\n")

        for i in self.main_class.features:
            # Busca todas as funções que não são padrão e nem a própria main.
            if isinstance(i, type_fields['Method']):
                if i.ident.name not in inbuilt_functions and i.ident.name != "main":
                    self.add_function(i, "main")

    def check_for_main_method(self):
        main_block = ()
        # Percorre todas as features da classe main, em busca do método main.
        for feature in self.main_class.features:
            if isinstance(feature, type_fields['Method']) and feature.ident.name == 'main':
                main_block = feature
                break

        if main_block ==():
            raise Error("Não existe metodo main. O programa é inválido") 

        # Checar o metodo main para encontrar funções chamadas, aqui pode ter mais de um elemento
        for elements in main_block.expr:
            for execute_method in elements:
                # print("main functions ----------------")
                # print(execute_method)
                # print("END ----------------\n")
                if isinstance(execute_method, type_fields['FunctCall']):
                    finalParam = ""
                    for param in execute_method.params:
                        finalParam += str(param) + " "
                    s = "response : int = " + execute_method.ident.name + " " + finalParam
                    self.write(s, 1)
                    
                    self.add_statement(execute_method)
        
def codegen(sourcefile):
    codeGen = CodeGen(sourcefile)
    codeGen.check_for_Main_class()   
    codeGen.check_for_main_method()
    codeGen.analyzer_functions()
    
if __name__ == "__main__":
    import sys
    sourcefile = sys.argv[1]
    codegen(sourcefile)