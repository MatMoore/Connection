'''Unit tests for parser'''

import unittest
from scripting import parser
from scripting import lexer
from scripting.parser import Node

script1 = '''score {
	add (territory) (captures)
}'''

tree1 = Node(
	'functioncall',
	[Node('block',
		[Node('functioncall',
			[
			Node('functioncall',[],'territory'),
			Node('functioncall',[],'captures')
			],
			'add')
		])
	],
	'score')

script2 = '''score {
	$foo
	$bar
	$a = 'b'
}'''

tree2 = Node(
	'functioncall',
	[
		Node('block',[
			Node('statement_list',
				[
					Node('variable',[],'foo'),
					Node('variable',[],'bar'),
					Node('assignment',[Node('literal',[],'b')],'a')
				]
			)
		])
	],
	'score')

script3 = "$a = $b = $c = $d"

tree3 = Node(
	'assignment',
	[
		Node('assignment',
			[
			Node('assigment',
				[
					Node('variable',[],'d'),
				],
				'c'
			)
			],
			'b'
		)
	],
	'a'
)

class ParserTest(unittest.TestCase):
	def setUp(self):
		self.lexer = lexer.setup()
		self.parser = parser.setup()

	def test1(self):
		tree = self.parser.parse(script1,lexer=self.lexer,debug=1)
		self.assertEqual(tree,tree1)

	def test2(self):
		tree = self.parser.parse(script2,lexer=self.lexer,debug=1)
		self.assertEqual(tree,tree2)

#	def test3(self):
#		tree = self.parser.parse(script3,lexer=self.lexer,debug=1)
#		self.assertEqual(tree,tree3)

def suite():
	suite1 = unittest.makeSuite(ParserTest)
	alltests = unittest.TestSuite((suite1))
	return alltests
