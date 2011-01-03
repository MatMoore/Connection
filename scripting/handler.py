if __name__=='__main__':
	# Add the parent package modules to the search path
	import sys
	sys.path = ['..'] + sys.path

import operator
import multilogger
import random

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

	def _eval_args(self,node,*args):
		return [self._handle(i,*args) for i in node.children]

	def _func_add(self,node,*args):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args))

		return sum(a)

	def _func_multiply(self,node,*args):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args))

		return reduce(operator.mul,a,1)

	def _func_subtract(self,node,*args):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args))

		if len(a) != 2:
			warning('subtract can only take two arguments')

		first,second = a

		return first - second

	def _func_divide(self,node,*args):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args))

		if len(a) != 2:
			warning('divide can only take two arguments')

		first,second = a

		return first / second

	def _func_dividef(self,node,*args):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args))

		if len(a) != 2:
			warning('dividef can only take two arguments')

		first,second = a

		return first / float(second)

	def _func_mod(self,node,*args):
		# If an argument is a list, flatten it first
		a = flatten(self._eval_args(node,*args))

		if len(a) != 2:
			warning('mod can only take two arguments')

		first,second = a

		return first % float(second)

	def _func_print(self,node,*args):
		a = '\n'.join(map(str,self._eval_args(node,*args)))
		info(a)

	def _func_all(self,node,*args):
		a = self._eval_args(node,*args)
		return all(a)

	def _func_any(self,node,*args):
		a = self._eval_args(node,*args)
		return any(a)

	def _func_if(self,node,*args):

		if len(node.children) not in (2,3):
			warning('Too many arguments to "if"')
			return None

		condition = node.children[0]
		success = node.children[1]

		if len(node.children) > 2 :
			fail = node.children[2]
		else:
			fail = None

		if self._handle(condition,*args):
			return self._handle(success,*args)
		else:
			if fail is None:
				return False
			else:
				return self._handle(fail,*args)

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
