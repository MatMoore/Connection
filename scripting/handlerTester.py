'''Unit tests for handler'''
if __name__=='__main__':
	# Add the parent package modules to the search path
	import sys
	sys.path = ['..'] + sys.path
import unittest
import handler
from parser import Node

# 1 + 1
tree1 = Node(
	'functioncall',
	[
		Node('literal',[],1),
		Node('literal',[],1),
	],
	'add'
)
ans1 = 2

# (3 * 4) / 2
tree2 = Node(
	'functioncall',
	[
		Node(
			'functioncall',
			[
				Node('literal',[],3),
				Node('literal',[],4),
			],
			'multiply'
		),
		Node('literal',[],2),
	],
	'divide'
)
ans2 = 6

tree3 = Node('literal',[],'bananas')
ans3 = 'bananas'

# 3 % 2
tree4 = Node(
	'functioncall',
	[
		Node('literal',[],3),
		Node('literal',[],2),
	],
	'mod'
)
ans4 = 1

# 7/2
tree5 = Node(
	'functioncall',
	[
		Node('literal',[],7),
		Node('literal',[],2),
	],
	'divide'
)
ans5 = 3

# 3-2
tree6 = Node(
	'functioncall',
	[
		Node('literal',[],3),
		Node('literal',[],2),
	],
	'subtract'
)
ans6 = 1

tree7 = Node(
	'functioncall',
	[
		Node('literal',[],1),
		Node('literal',[],2),
	],
	'if'
)
ans7 = 2

tree8 = Node(
	'functioncall',
	[
		Node('literal',[],0),
		Node('literal',[],2),
		Node('literal',[],3),
	],
	'if'
)
ans8 = 3

tree9 = Node(
	'statement_list',
	[
		Node('assignment',[Node('literal',[],1)],'foo'),
		Node(
			'functioncall',
			[
				Node('literal',[],0),
				Node('assignment',[Node('literal',[],2)],'foo'),
				Node('literal',[],3),
			],
			'if'
		),
		Node('variable',[],'foo'),
	]
)
ans9 = 1

tree10 = Node(
	'statement_list',
	[
		Node('assignment',[Node('literal',[],1)],'foo'),
		Node(
			'functioncall',
			[
				Node('literal',[],1),
				Node('assignment',[Node('literal',[],2)],'foo'),
				Node('literal',[],3),
			],
			'if'
		),
		Node('variable',[],'foo'),
	]
)
ans10 = 2

tree = (tree1,tree2,tree3,tree4,tree5,tree6,tree7,tree8,tree9,tree10)
ans = (ans1,ans2,ans3,ans4,ans5,ans6,ans7,ans8,ans9,ans10)

def testn(n):
	def f(self):
		result = handler.Handler(tree[n])._handle(tree[n])
		self.assertEqual(result,ans[n])
	return f

class HandlerTest(unittest.TestCase):
	def setUp(self):
		pass

# Dynamically create the HandlerTest tests
for i in range(10):
	setattr(HandlerTest,'test'+str(i),testn(i))

def suite():
	suite1 = unittest.makeSuite(HandlerTest)
	alltests = unittest.TestSuite((suite1))
	return alltests

if __name__ == "__main__":
	unittest.main()
