alpha 	[A-Za-z_]
fl		(f|F|l|L)
ul		(u|U|l|L)*
digit		[0-9]
space 	[ ]
hex		[a-fA-F0-9]
exp		[Ee][+-]?{digit}+
%{
//int yylineno = 1;
char datatype[100] = "dummy";
int tl;
int scope_val = 0;
static int scope = 0;
char next;
int initialised=0;
int get_scope();
#include <stdio.h>
#include <string.h> 

typedef struct stack
{
	int val;
	struct stack* next;
}stack;
stack* scope_stk;



%}

%%	
\n   { yylineno++; }

"//".*\n { printf("single line comment\n");}
\/\*(.*\n)*.*\*\/ {printf("multi line comment\n");};

"#include<"({alpha})*".h>" {}
"#include\""({alpha})*".h\"" {}

"#define"({space})""({alpha})""({alpha}|{digit})*""({space})""({digit})+"" 			{ return DEFINE;}
"#define"({space})""({alpha}({alpha}|{digit})*)""({space})""(({digit}+)\.({digit}+))"" 		{ return DEFINE;}
"#define"({space})""({alpha}({alpha}|{digit})*)""({space})""({alpha}({alpha}|{digit})*)"" 	{ return DEFINE;}

{digit}+    				{  insertToConstTable(yytext, yylineno, "INT"); return CONSTANT; }
({digit}+)\.({digit}+) 			{  insertToConstTable(yytext, yylineno, "FLOAT"); return CONSTANT; }
0[xX]{hex}+{ul}?			{  insertToConstTable(yytext, yylineno, "FLOAT"); return CONSTANT; }
{digit}+{ul}?				{  insertToConstTable(yytext, yylineno, "FLOAT"); return CONSTANT; }
'(\\.|[^\\'])+'				{  insertToConstTable(yytext, yylineno, "FLOAT"); return CONSTANT; }
{digit}+{exp}{fl}?			{  insertToConstTable(yytext, yylineno, "FLOAT"); return CONSTANT; }
{digit}*"."{digit}+({exp})?{fl}?	{  insertToConstTable(yytext, yylineno, "FLOAT"); return CONSTANT; }
{digit}+"."{digit}*({exp})?{fl}?	{  insertToConstTable(yytext, yylineno, "FLOAT"); return CONSTANT; }

{alpha}?\"(\\.|[^\\"])*\"		{  insertToConstTable(yytext, yylineno, "STRING"); return STRING_LITERAL; } 

"->"			{  return PTR_OP; }
"++"			{  return INC_OP; }
"--"			{  return DEC_OP; }
"<<"			{  return LEFT_OP; }
">>"			{  return RIGHT_OP; }
"<="			{  return LE_OP; }
">="			{  return GE_OP; }
"=="			{  return EQ_OP; }
"!="			{  return NE_OP; }
"&&"			{  return AND_OP; }
"||"			{  return OR_OP; }
"*="			{  return MUL_ASSIGN; }
"/="			{  return DIV_ASSIGN; }
"%="			{  return MOD_ASSIGN; }
"+="			{  return ADD_ASSIGN; }
"-="			{  return SUB_ASSIGN; }
"<<="			{  return LEFT_ASSIGN; }
">>="			{  return RIGHT_ASSIGN; }
"&="			{  return AND_ASSIGN; }
"^="			{  return XOR_ASSIGN; }
"|="			{  return OR_ASSIGN; }

"auto"		{ return AUTO; }
"break"		{ return BREAK; }
"char"		{ return CHAR; }
"const"		{ return CONST; }
"continue"		{ return CONTINUE; }
"do"			{ return DO; }
"double"		{ return DOUBLE; }
"else"		{ return ELSE; }
"extern"		{ return EXTERN; }
"float"		{ strcpy(datatype, "FLOAT"); tl = yylineno; return FLOAT; }
"for"			{ return FOR; }
"if"			{ return IF; }
"int"			{ strcpy(datatype, "INT"); tl = yylineno; return INT; }
"long"		{ return LONG; }
"register"		{ return REGISTER; }
"return"		{ return RETURN; }
"short"		{ return SHORT; }
"signed"		{ return SIGNED; }
"sizeof" 		{ return SIZEOF; }
"static"		{ return STATIC; }
"struct"		{ return STRUCT; }
"typedef"		{ return TYPEDEF; }
"union"		{ return UNION; }
"unsigned"		{ return UNSIGNED; }
"void"		{ return VOID; }
"while"		{ return WHILE; }


";"			{  strcpy(datatype, "dummy"); return(';'); }
("{"|"<%")		{  	scope++;
				//initState();
				push(scope);
				return('{'); }
("}"|"%>")		{  
				pop();
				return('}'); }
","			{  return(','); }
":"			{  return(':'); }
"="			{  return('='); }
"("			{  return('('); }
")"			{  return(')'); }
("["|"<:")		{  return('['); }
("]"|":>")		{  return(']'); }
"."			{  return('.'); }
"&"			{  return('&'); }
"!"			{  return('!'); }
"~"			{  return('~'); }
"-"			{  return('-'); }
"+"			{  return('+'); }
"*"			{  return('*'); }
"/"			{  return('/'); }
"%"			{  return('%'); }
"<"			{  return('<'); }
">"			{  return('>'); }
"^"			{  return('^'); }
"|"			{  return('|'); }
"?"			{  return('?'); }
"printf"|"scanf"	{  return IDENTIFIER; }
"main" 			{ return IDENTIFIER; }
{alpha}({alpha}|{digit})*    		{  
						if(strcmp(datatype, "dummy")==0)
							return IDENTIFIER;
						else 
						{
							scope_val = get_scope();
							insertToHash(yytext,datatype,yylineno,scope_val);
							return IDENTIFIER; 
						}
					}
[ \t\v\n\f]		{  }
.			{ /* ignore bad characters */ }
%%



void push(int scope)
{
	stack *new = NULL;
	new = (stack*)malloc(sizeof(stack));
	new->val = scope;
	new->next = scope_stk;
	scope_stk = new;
}

void pop()
{
	stack * temp = scope_stk;
	scope_stk = temp->next;
	free(temp);
}

int get_scope()
{
	return scope_stk->val;
}

struct cnode
{
	char num[50];
	int lno;
	char type[20];
};
struct cnode ctable[100];
int ccount = 0;

void initState(){
	printf("called\n");
	if(initialised==0){
		scope_stk = (stack*)malloc(sizeof(stack));
		scope_stk->val = 0;
		scope_stk->next = NULL;
		initialised=1;
	}
	
	
}

void insertToConstTable(char *num, int l, char *type)
{
	strcpy(ctable[ccount].num, num);
	strcpy(ctable[ccount].type, type);
	ctable[ccount].lno = l;
	ccount++;
}

struct node
{
	char token[100];
    	char attr[100];
    	int line;
    	int scope;
	struct node *next;
};

struct hash
{
	struct node *head;
	int hash_count;
};

struct hash hashTable[1000];
int hc = 1000;

struct node * createNode(char *token, char *attr, int l, int scope)
{
	struct node *newnode;
	newnode = (struct node *) malloc(sizeof(struct node));
	strcpy(newnode->token, token);
	strcpy(newnode->attr, attr);
	newnode->line = l; 
	newnode->scope = scope;
	newnode->next = NULL;
	return newnode;
}

int hashIndex(char *token)
{
	int hi=0;
	int l,i;
	for(i=0;token[i]!='\0';i++)
	{
		hi = hi + (int)token[i];
	}
	hi = hi%hc;
	return hi;
}

void insertToHash(char *token, char *attr, int l, int scope)
{
	int flag=0;
	int hi;
	hi = hashIndex(token);
	struct node *newnode = createNode(token, attr, l, scope);
	if (hashTable[hi].head==NULL)
	{
		hashTable[hi].head = newnode;
	        hashTable[hi].hash_count = 1;
	        return;
	}
	struct node *myNode;
    	myNode = hashTable[hi].head;
	while (myNode != NULL)
    	{
        	if (strcmp(myNode->token, token)==0)
        	{
            		flag = 1;
            		if(strcmp(myNode->attr, attr)!=0)
            		{
            			strcpy(myNode->attr, attr);
            		}
            		break;
        	}
        	myNode = myNode->next;
    	}
	if(!flag)
	{
		newnode->next = (hashTable[hi].head);
		hashTable[hi].head = newnode;
		hashTable[hi].hash_count++;
	}
	return;
}

char* getvalue(int line, char* type)
{
	int i=0;
	if(strcmp(type, "PROCEDURE") == 0)
		return "";
	while(i<ccount)
	{
		if(line == ctable[i].lno)
		{
			if(strcmp(type, ctable[i].type) == 0)
				return ctable[i].num;
		}
		i++;
	}
	return "";
}

void display()
{
    	struct node *myNode;
    	char *val;
    	int i,j, k=1;
    	printf("\nSymbol Table\n");
    	printf("\nToken \t\t|\tToken Type \t\t|\tLine no.\t\t|\tValue\t\t|\tScope\t\n");
    	for (i = 0; i < hc; i++)
    	{
        	if (hashTable[i].hash_count == 0)
            		continue;
        	myNode = hashTable[i].head;
        	if (!myNode)
            		continue;
        	while (myNode != NULL)
        	{
            		
            		printf("%s\t\t\t", myNode->token);
            		printf("%s\t\t\t", myNode->attr);
            		val = getvalue(myNode->line, myNode->attr);
            		if(i!=0)
            		{
	            		printf("\t%d\t\t",myNode->line);
	            		printf("\t\t%s",val);
	            		printf("\t\t\t%d",myNode->scope);
            		}
            		printf("\n");
            		myNode = myNode->next;
        	}
	}
   	return;
}

yywrap()
{
	return(1);
}
