#!/usr/bin/python
# Unit test for geometry.py

import unittest
from geometry import *

class SquareGridTest(unittest.TestCase):
	def setUp(self):
		self.grid = RectangularGrid(9,9,1)

	def testLen(self):
		self.assertEqual(len(self.grid), 81)

	def testSize(self):
		self.assertEqual(self.grid.size(), (0,0,8,8))

class RectangularGridTest(unittest.TestCase):
	def setUp(self):
		self.grid = RectangularGrid(9,9,2)


class EmptyGridTest(RectangularGridTest):
	def testLen(self):
		self.assertEqual(len(self.grid), 81)

	def testSize(self):
		self.assertEqual(self.grid.size(), (0,0,16,8))

	def testPointsInTurn(self):
		for i in range(0,17,2):
			for j in range(0,9):
				self.assertTrue(self.grid.get_point(i,j) is None)

	def testPointsIterator(self):
		n = 0
		for pos,val in self.grid.get_points():
			x,y = pos
			n += 1
			self.assertTrue(x in (0,2,4,6,8,10,12,14,16))
			self.assertTrue(y in (0,1,2,3,4,5,6,7,8))
			self.assertTrue(val is None)
		self.assertEqual(n, 81)

class SetValueTest(RectangularGridTest):
	def testPointsInTurn(self):
		for i in range(0,17,2):
			for j in range(9):
				self.assertTrue(self.grid.get_point(i,j) is None)
				self.grid.set_point(i,j,1)
				self.assertEqual(self.grid.get_point(i,j), 1)

class NeighbourTest(RectangularGridTest):
	def testConnections(self):
		for i in range(0,17,2):
			for j in range(9):
				conns = frozenset(self.grid.neighbours(i,j))
				required = set()
				if (i > 0):
					required.add((i-2,j))
				if (i < 16):
					required.add((i+2,j))
				if (j > 0):
					required.add((i,j-1))
				if (j < 8):
					required.add((i,j+1))
				self.assertEqual(conns, required)

def suite():
	tests = (SquareGridTest,NeighbourTest,EmptyGridTest,SetValueTest)
	return unittest.TestSuite(map(unittest.makeSuite,tests))
#	suite1 = unittest.makeSuite(NeighbourTest)
#	suite2 = unittest.makeSuite(NeighbourTest)
#	suite3 = unittest.makeSuite(EmptyGridTest)
#	suite4 = unittest.makeSuite(SetValueTest)
#	alltests = unittest.TestSuite((suite1,suite2,suite3,suite4))
#	return alltests

if __name__ == "__main__":
	unittest.main()
