'''Unit tests for lexer'''

from scripting import lexer
import unittest
import ply.lex as lex

script1 = '''score {
	add (territory) (captures)
}'''
types1 = ('NAME','LBRACE','NEWLINE','NAME','LPAREN','NAME','RPAREN','LPAREN','NAME','RPAREN','NEWLINE','RBRACE','END')
values1 = ('score','{','\n','add','(','territory',')','(','captures',')','\n','}','eof')

script2 = '''$test_param:string
$creator = 'Mat'
$version = 0.1$int=1'''
types2 = ('VARIABLE','IS_A','NAME','NEWLINE','VARIABLE','ASSIGN','STRING','NEWLINE','VARIABLE','ASSIGN','FLOAT','VARIABLE','ASSIGN','INTEGER','END')
values2 = ('test_param',':','string','\n','creator','=','Mat','\n','version','=',0.1,'int','=',1,'eof')

class LexerTest(unittest.TestCase):
	def setUp(self):
		self.lexer = lexer.setup()

	def test1(self):
		self.lexer.input(script1)

		for i,token in enumerate(self.lexer):
			print token
			self.assertEqual(types1[i],token.type)
			self.assertEqual(values1[i],token.value)

	def test2(self):
		self.lexer.input(script2)

		for i,token in enumerate(filter(lambda t: t.type != 'WHITESPACE', self.lexer)):
			print token
			self.assertEqual(types2[i],token.type)
			self.assertEqual(values2[i],token.value)


def suite():
	suite1 = unittest.makeSuite(LexerTest)
	alltests = unittest.TestSuite((suite1))
	return alltests
