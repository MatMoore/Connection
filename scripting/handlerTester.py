'''Unit tests for handler'''
import sys
if __name__=='__main__':
	# Add the parent package modules to the search path
	sys.path = ['..'] + sys.path
import unittest
import handler
import testCases

def testn(tree,ans,docstring=None):
	def f(self):
		result = handler.Handler(tree)._handle(tree)
		self.assertEqual(result,ans)

	if docstring is None:
		docstring = '; '.join(tree.indent().split('\n'))

	f.__doc__ = docstring
	return f

class HandlerTest(unittest.TestCase):
	pass

# Dynamically create the HandlerTest tests
for i,testCase in enumerate(testCases.syntaxTree()):
	tree,ans,name = testCase
	setattr(HandlerTest,'test'+str(i)+'_'+name,testn(tree,ans,name))

def suite():
	suite1 = unittest.makeSuite(HandlerTest)
	alltests = unittest.TestSuite((suite1))
	return alltests

if __name__ == "__main__":
	for i in sys.argv[1:]:
		# Try and run the specified script
		script = ''.join(open(i).readlines())
		handler.run(script,debug=True)
	if not sys.argv[1:]:
		unittest.main()
