import ply.lex as lex

tokens = (
	'NAME', # function names
	'STRING', # single quoted strings
	'VARIABLE',
	'IS_A', # used to declare types (for validating input only)
	'LPAREN',
	'RPAREN',
	'LBRACE',
	'RBRACE',
	'NEWLINE',
	'INTEGER',
	'FLOAT',
	'ASSIGN',
	'END',
)

def t_FLOAT(t):
	'''-?\d+\.\d*'''
	t.value = float(t.value)
	return t

def t_INTEGER(t):
	'''-?\d+'''
	t.value = int(t.value)
	return t

def t_STRING(t):
	'''\'[^\']*\''''
	t.value = t.value[1:-1]
	return t

def t_VARIABLE(t):
	'''\$[a-zA-Z_][a-zA-Z0-9_]*'''
	t.value = t.value[1:]
	return t

def t_NAME(t):
	'''[a-zA-Z_][a-zA-Z0-9_]*'''
	return t

def t_ASSIGN(t):
	'''='''
	return t

def t_IS_A(t):
	''':'''
	return t

def t_NEWLINE(t):
	r'\n+'
	return t

def t_comment(t):
	"\s*\\043[^\n]*"
	pass

#def t_WHITESPACE(t):
#	"\s+"
#	return t

def t_error(t):
	print 'Unknown character %s' % t.value[0]
	t.lexer.skip(1)

def t_LPAREN(t):
	'''\('''
	return t

def t_RPAREN(t):
	'''\)'''
	return t

def t_LBRACE(t):
	'''\{'''
	return t

def t_RBRACE(t):
	'''\}'''
	return t

t_ignore = '\t '

def setup():
	return MyLexer(lex.lex())

class MyLexer:
	def __init__(self,lexer):
		self.lexer = lexer
		self.done = False

	def input(self,script):
		self.lexer.input(script)

	def __iter__(self):
		while True:
			t = self.token()
			if t is None:
				raise StopIteration
			yield t

	def end(self):
		end = lex.LexToken()
		end.type = 'END'
		end.value = 'eof'
		end.lineno = -1
		end.lexpos = -1
		self.done = True
		return end

	def token(self):
		next = self.lexer.token()
		if next is None:
			if self.done: return None
			else: return self.end()
		else: return next
