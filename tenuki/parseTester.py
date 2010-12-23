#!/usr/bin/python
# Unit tests for parser.py

import unittest
from parser import parse,context,tokens,ParseError

class ParseTest(unittest.TestCase):
	def testSimpleExpression(self):
		t = context(tokens('1 + 1'))
		ans = parse(t)
		self.assertEqual(ans,2)

	def testMissingOperand1(self):
		t = context(tokens('1 +'))
		self.assertRaises(ParseError,parse,t)

	def testMissingOperand2(self):
		t = context(tokens('+ 1'))
		self.assertRaises(ParseError,parse,t)

	def testSyntaxError1(self):
		self.assertRaises(ParseError,tokens,'1+1')

	def testSyntaxError2(self):
		self.assertRaises(ParseError,tokens,'1 - 1')

def suite():
	suite1 = unittest.makeSuite(ParseTest)
	alltests = unittest.TestSuite((suite1))
	return alltests

if __name__ == "__main__":
	unittest.main()
