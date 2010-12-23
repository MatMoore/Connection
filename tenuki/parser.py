'''Tenuki parser which uses Pratt's algorithm for Top-Down Parsing. (Pratt V. R. 1976: Top down operator precedence, Proceedings of the 1st annual ACM SIGACT-SIGPLAN symposium on Principles of programming languages p41-51) See also http://effbot.org/zone/simple-top-down-parsing.htm for a description in python.'''

import re

class ParseError(Exception): pass

class LiteralToken:
	leftBindingPower = 0

	def __init__(self,value):
		self.value = value

	def nullDenotation(self,context):
		return self.value

	def leftDenotation(self,context,left):
		raise ParseError('Literal cannot appear in the middle of an expression')

	def __repr__(self):
		return 'Literal '+str(self.value)

class AddToken:
	leftBindingPower = 10

	def nullDenotation(self,context):
		raise ParseError('Missing left operand for operator +')

	def leftDenotation(self,context,left):
		right = parse(context,self.leftBindingPower)

		if right is None:
			raise ParseError('Missing right operand for operator +')

		return left + right

	def __repr__(self):
		return '[Add token]'

def parse(context,rightBindingPower=0):
		'''Parse from left to right everything that binds tighter than rightBindingPower'''
		try:
			token,nextToken  = context.next()
		except StopIteration:
			return None

		# Get the value of the first token
		left = token.nullDenotation(context)

		# While the following tokens have sufficient binding power,
		# feed them the left hand side and compute the resulting value
		try:
			while nextToken is not None and rightBindingPower < nextToken.leftBindingPower:
				token, nextToken = context.next()
				left  = token.leftDenotation(context,left)

		except StopIteration: return left
		return left

def context(tokens):
	'''Return an iterator over the tokens'''
	return doubles(iter(tokens))

#class Tokeniser():
#
#	def __init__(self):
#		self.tokens = {}
#		self.tokenProperties = {
#			';':('Seperator',100,symbol),
#			',':('Seperator',100,symbol),
#			'{':'Begin',
#			'}':'End',
#			'"':'DoubleQuote',
#			'\'':'SingleQuote',
#			':':('Type',80,infix),
#			'^':'Exponent',
#			'*':'Multiply',
#			'/':'Divide',
#			'+':'Add',
#			'-':'Subtract',
#			'=':'Assign',
#			'==':'Equal',
#			'<':'Less',
#			'>':'Greater',
#			'!=':'Not'
#		}
#	}
#
#	def generateTokens(self, token):
#		pass
#
#	def tokens(self.script):
#		tokens = []
#		for line in script.split("\n"):
#			tokens.extend(map(self.generateToken,line.split()))
#		return tokens

def doubles(iterator):
	'''Return the current element, and the next element'''
	first = iterator.next()

	while True:
		try:
			second = iterator.next()
			yield first,second
		except StopIteration:
			yield first,None
			raise StopIteration
		first = second

def tokens(script):
	tokens = []
	floaty = re.compile('^\d+(\.\d+)?$')

	for line in script.split("\n"):
		for i in line.split():
			if floaty.match(i):
				tokens.append(LiteralToken(float(i)))
			elif i == '+':
				tokens.append(AddToken())
			else:
				raise ParseError('Unrecognised token: '+i)
	return tokens
