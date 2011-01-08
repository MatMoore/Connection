if __name__=='__main__':
	# Add the parent package modules to the search path
	import sys
	sys.path = ['..'] + sys.path

import operator
import multilogger
import random
import parser
import lexer

def run(script,debug=False):
	l = lexer.setup()
	p = parser.setup()
	tree = p.parse(script,lexer=l,debug=debug)
	if tree is None:
		error('Cannot parse script')
		return
	if debug:
		print tree.indent()
	Handler(tree)

def flatten(li):
	'''Flatten li into a single list, allowing lists to be automatically unpacked when they are passed as arguments to functions which don't operate on lists'''
	new = []
	for i in li:
		if isinstance(i,list):
			new.extend(i)
		else:
			new.append(i)
	return new

class Handler(object):
	def __init__(self,syntaxTree):
		self.inputs = [] # Values set by user
		self.constants = {} # Values set by script writer
		self.variables = {} # Variables set as part of a game action
		self._each_stack = [] # Stack of "next" values populated while looping with the each function

		self._handle(syntaxTree)

	def _handle(self,node,game=None,player=None):
		'''Handle a node of the syntax tree'''
		try:
			method = getattr(self,'_handle_'+node.type)

		except AttributeError:
			warning('No handler "'+'_handle_'+node.type + '"')
			return None

		return method(node,game,player)

	def inputs(self):
		pass

	def run_action(self,action,game,player=None):
		'''Run a game action'''
		pass

	def _handle_declaration_list(self,node,game=None,player=None):
		for i in node.children:
			self._handle(i,game,player)

		return None

	def _handle_declaration(self,node,game=None,player=None):
		assert node.leaf is not None
		assert len(node.children) == 1

		name = node.leaf
		type = node.children[0].leaf
		self.inputs.append((name,type))

		return None

	def _handle_statement_list(self,node,game=None,player=None):
		'''Handle a list of statements. The value is the value of the last expression, or None if there weren't any.'''
		assert len(node.children)

		value = None

		for i in node.children:
			new_value = self._handle(i,game,player)
			if new_value is not None:
				value = new_value

		return value

	def _handle_literal(self,node,game=None,player=None):
		assert node.leaf is not None
		return node.leaf

	def _handle_assignment(self,node,game=None,player=None):
		assert node.leaf is not None
		assert len(node.children) == 1

		name = node.leaf
		value = self._handle(node.children[0],game,player)

		if game is None:
			if name in self.constants:
				warning('value for '+name+' already exists')

			self.constants[name] = value
		else:
			# If game is passed in, that means we are handling an action
			self.variables[(name,game)] = value

		return value

	def _handle_functioncall(self,node,game=None,player=None):
		assert isinstance(node.leaf, str)

		try:
			method = getattr(self,'_func_' + node.leaf)
		except AttributeError:
			error('no such function '+node.leaf)

		return method(node, game)

	def _handle_block(self,node,game=None,player=None):
		assert len(node.children) == 1

		return self._handle(node.children[0],game,player)

	def _handle_variable(self,node,game=None,player=None):
		'''Get the value of a variable. Note that variables defined inside actions do not persist between turns.'''
		assert isinstance(node.leaf,str)
		assert len(node.children) == 0

		name = node.leaf
		value = None

		# If game is passed in, that means we are handling an action
		if game is not None and (name,game) in self.variables:
			value = self.variables[(name,game)]

		if value is None and name in self.constants:
			value = self.constants[name]

		if value is None:
			error('variable '+name+' does not exist')

		return value

	def _eval_args(self,node,*args,**kwargs):
		return [self._handle(i,*args,**kwargs) for i in node.children]

	def _func_add(self,node,*args,**kwargs):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args,**kwargs))

		return sum(a)

	def _func_multiply(self,node,*args,**kwargs):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args,**kwargs))

		return reduce(operator.mul,a,1)

	def _func_subtract(self,node,*args,**kwargs):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args,**kwargs))

		if len(a) != 2:
			warning('subtract can only take two arguments')

		first,second = a

		return first - second

	def _func_divide(self,node,*args,**kwargs):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args,**kwargs))

		if len(a) != 2:
			warning('divide can only take two arguments')

		first,second = a

		return first / second

	def _func_dividef(self,node,*args,**kwargs):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args,**kwargs))

		if len(a) != 2:
			warning('dividef can only take two arguments')

		first,second = a

		return first / float(second)

	def _func_mod(self,node,*args,**kwargs):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args,**kwargs))

		if len(a) != 2:
			warning('mod can only take two arguments')

		first,second = a

		return first % float(second)

	def _func_print(self,node,*args,**kwargs):
		a = '\n'.join(map(str,self._eval_args(node,*args,**kwargs)))
		info(a)

	def _func_all(self,node,*args,**kwargs):
		a = flatten(self._eval_args(node,*args,**kwargs))
		return all(a)

	def _func_any(self,node,*args,**kwargs):
		a = flatten(self._eval_args(node,*args,**kwargs))
		return any(a)

	def _if(self,condition,success,fail,*args,**kwargs):
		if self._handle(condition,*args,**kwargs):
			if success is None:
				return None
			else:
				return self._handle(success,*args,**kwargs)
		else:
			if fail is None:
				return None
			else:
				return self._handle(fail,*args,**kwargs)

	def _each(self,l,block,*args,**kwargs):
		self._each_stack.append(None)
		for i in l:
			self._each_stack[-1] = i
			result = self._handle(block,*args,**kwargs)
		self._each_stack.pop()
		return result

	def _func_each(self,node,*args,**kwargs):
		if len(node.children) < 2:
			error('not enough arguments to "each"')
			return None
		elif len(node.children) > 2:
			warning('unexpected arguments to "each"')

		l = self._handle(node.children[0],*args,**kwargs)

		return self._each(l,node.children[1],*args,**kwargs)

	def _next(self):
		if not self._each_stack:
			error('next called outside a loop')
			return None
		return self._each_stack[-1]

	def _func_next(self,node,*args,**kwargs):
		if node.children:
			warning('unexpected arguments to "next"')

		return self._next()

	def _func_if(self,node,*args,**kwargs):

		if len(node.children) not in (2,3):
			warning('Too many arguments to "if"')
			return None

		condition = node.children[0]
		success = node.children[1]

		if len(node.children) > 2 :
			fail = node.children[2]
		else:
			fail = None

		return self._if(condition,success,fail,*args,**kwargs)

	def _func_unless(self,node,*args,**kwargs):

		if len(node.children) != 1:
			warning('Incorrect number of arguments to "unless"')
			return None

		condition = node.children[0]
		success = node.children[1]

		return self._if(condition,None,success,*args,**kwargs)

	def _func_not(self,node,*args,**kwargs):
		a = flatten(self._eval_args(node,*args,**kwargs))
		if len(a) != 1:
			warning('not can only take one argument')

		if not node.children: return False

		return not a[0]

	def _func_min(self,node,*args,**kwargs):
		a = flatten(self._eval_args(node,*args,**kwargs))
		return min(a)

	def _func_max(self,node,*args,**kwargs):
		a = flatten(self._eval_args(node,*args,**kwargs))
		return max(a)

	def _func_range(self,node,*args,**kwargs):
		a = flatten(self._eval_args(node,*args,**kwargs))
		if len(a) > 3:
			warning('too many arguments to "range"')
		return list(range(*a))

	def _func_equal(self,node,*args,**kwargs):
		'''All args are the same'''
		a = self._eval_args(node,*args,**kwargs)
		return all([j==i for i,j in zip(a,a[1:])])

	def _func_less(self,node,*args,**kwargs):
		'''Each arg is less than the ones preceeding it'''
		a = self._eval_args(node,*args,**kwargs)
		return all([j<i for i,j in zip(a,a[1:])])

	def _func_more(self,node,*args,**kwargs):
		return self._func_greater(node,*args,**kwargs)

	def _func_greater(self,node,*args,**kwargs):
		'''Each arg is greater than the ones preceeding it'''
		a = self._eval_args(node,*args,**kwargs)
		return all([j>i for i,j in zip(a,a[1:])])

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
