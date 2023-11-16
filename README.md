# Mini-C-Compiler
Constructing C compiler for IF, WHILE and FOR constructs using Lex and Yacc


## Design

### Symbol table: 
First when the lex file generates the tokens then with the grammar we check if it is variable declaration or variable assignment. If it is either of one then we add it to the symbol table. Symbol table is being stored as the structure. The structure consists of the fields which are the name of the variable, type of variable(int, float and char), value which is assigned to the variable and scope of the variable. 

### Abstract Syntax tree: 
Abstract syntax trees consist of nodes and childrens as its code. Those nodes consists of the operators or operands. mainly parents contain the operators and children have operands. These are interconnected to form a tree. This tree starts from ‘main’ followed by the code as the children. The nodes below ‘main’ consists of code from main function in C code. Then we write a display() function to display the code.

### Intermediate code generation: 
Whenever we encounter the statements, we match it with the grammar and we print the grammar in the form of three address code accordingly. Whenever we have to print If or while or for, we take care of printing goto, labels and other required statements 

### Code optimization: 
We do two types of optimization: 
  #### 1. Constant folding
  In this we try to see if there are only numbers on the RHS. If it has only numbers, then we solve those equations and replace operands and operators with the final output so it shouldn’t create much burden during run time. 
#### 2. Dead code elimination
  In this we try to remove the C statements which are not used further. We keep track of the temporary variables and C variables which are not used and we eliminate those.

### Error handling: 
In this we add a word ‘error’ in the statements part of the grammar. Whenever we get an error it ignores the error, calls the ‘yyerror’ function and continues to parse after next ‘;’ which is the indication of end of the statement in C.

### Target code generation: 
Our target code is ARM assembly code. We keep when to call load and store of C variables. For temporary variables, we store all those directly into registers. The register allocation used here is forward lookup . 
