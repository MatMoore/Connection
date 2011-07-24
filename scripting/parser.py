from lexer import tokens
import ply.yacc as yacc

class Node:
	def __init__(self,type,children=None,leaf=None):
		self.type = type
		self.leaf = leaf
		if children:
			self.children = children
		else:
			self.children = []

	def indent(self,levels=0):
		leaf = ''
		if self.leaf is not None: leaf = repr(self.leaf)
		root = '  ' * levels + self.type + ' ' + leaf
		children = [i.indent(levels+1) for i in self.children]
		return '\n'.join([root] + children)

	def __repr__(self):
		return self.indent()

	def __eq__(self,other):
		if self.type != other.type:
			return False
		if self.leaf != other.leaf:
			return False
		if self.children != other.children:
			return False
		return True

def p_syntax(p):
	'''syntax  : statement-list END
	           | declaration-list NEWLINE statement-list END'''
	if len(p) == 3:
		p[0] = p[1]
	else:
		p[0] = Node('syntax',[p[1],p[3]])

def p_declaration_list(p):
	'''declaration-list : declaration
	                    | declaration-list NEWLINE declaration'''
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = Node('declaration_list',[],p[1].children + p[2].children)

def p_declaration(p):
	'''declaration : NAME IS_A type'''
	p[0] = Node('declaration',[p[3]],p[1])

def p_type(p):
	'''type : NAME'''
	p[0] = Node('type',[],p[1])

def p_statement_list(p):
	'''statement-list : expression
	                   | assignment
	                   | statement-list NEWLINE expression
	                   | statement-list NEWLINE assignment
	                   | statement-list NEWLINE'''
	if len(p) < 4:
		p[0] = p[1]

	else:
		if p[1].type == 'statement_list':
			previous = p[1].children
		else:
			previous = [p[1]]

		p[0] = Node('statement_list',previous + [p[3]])

def p_expression(p):
	'''expression : functioncall
	              | literal'''
	#p[0] = Node('expression',[p[1]])
	p[0] = p[1]

def p_variable(p):
	'''expression : VARIABLE'''
	p[0] = Node('variable',[],p[1])

def p_literal(p):
	'''literal    : STRING
	              | FLOAT
	              | INTEGER'''
	p[0] = Node('literal',[],p[1])

def p_assignment(p):
	'''assignment : VARIABLE ASSIGN subexpression'''
	p[0] = Node('assignment',[p[3]],p[1])

def p_functioncall(p):
	'''functioncall : NAME arglist
	                | NAME'''
	if len(p) == 2:
		p[0] = Node('functioncall',[],p[1])
	else:
		p[0] = Node('functioncall',p[2].children,p[1])

def p_arglist(p):
	'''arglist : argument
	           | arglist argument'''
	if len(p) == 2:
		p[0] = Node('arglist',[p[1]])
	else:
		p[0] = Node('arglist',p[1].children + [p[2]])

def p_argument(p):
	'''argument : block
	            | subexpression'''
	#p[0] = Node('argument',[p[1]])
	p[0] = p[1]

def p_subexpression(p):
	'''subexpression : LPAREN functioncall RPAREN
	                | literal
	                | assignment'''
	if len(p) == 2:
		#p[0] = Node('expression',[p[1]])
		p[0] = p[1]
	else:
		#p[0] = Node('expression',[p[2]])
		p[0] = p[2]

def p_subexpression_variable(p):
	'''subexpression : VARIABLE'''
	p[0] = Node('variable',[],p[1])

def p_block(p):
	'''block : LBRACE statement-list RBRACE'''
	p[0] = Node('block',[p[2]])

def p_actiondef(p):
	'''actiondef : ACTION NAME NEWLINE block'''
	p[0] = Node('action',[p4],p[1])

def p_error(p):
	if p is None:
		print 'Unexpected end of file'
		return
	if p.type  == 'NEWLINE':
		print 'ignoring whitespace'
		yacc.errok()
	else:
		print 'Unexpected token %s' % p.type

def setup():
	return yacc.yacc()

if __name__ == '__main__':
	setup()
