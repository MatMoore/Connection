#!/usr/bin/python
# Unit test for geometry.py

import unittest
from geometry import *

class SquareGridTest(unittest.TestCase):
	def setUp(self):
		self.grid = RectangularGrid(9,9,1)

	def testLen(self):
		assert len(self.grid) == 81

	def testSize(self):
		assert self.grid.size() == (0,0,8,8)

class RectangularGridTest(unittest.TestCase):
	def setUp(self):
		self.grid = RectangularGrid(9,9,2)

	def testLen(self):
		assert len(self.grid) == 81

	def testSize(self):
		assert self.grid.size() == (0,0,16,8)

class EmptyGridTest(RectangularGridTest):
	def testPointsInTurn(self):
		for i in range(9):
			for j in range(0,17,2):
				assert self.grid.get_point(i,j) is None

	def testPointsIterator(self):
		n = 0
		for pos,val in self.grid.points():
			x,y = pos
			n += 1
			assert x in (0,2,4,6,8,10,12,14,16)
			assert y in (0,1,2,3,4,5,6,7,8)
			assert val is None
		assert n == 81

class SetValueTest(RectangularGridTest):
	def testPointsInTurn(self):
		for i in range(9):
			for j in range(0,17,2):
				assert self.grid.get_point(i,j) is None
				self.grid.set_point(i,j,1)
				assert self.grid.get_point(i,j) == 1

class NeighbourTest(RectangularGridTest):
	def testConnections(self):
		for i in range(9):
			for j in range(0,17,2):
				conns = frozenset(self.grid.neighbours(i,j))
				required = set()
				if (i > 0):
					required.add((i-1,j))
				elif (i < 8):
					required.add((i+1,j))
				if (j > 0):
					required.add((i,j-2))
				elif (j < 15):
					required.add((i,j+2))
				assert conns = required

def suite():
	suite1 = unittest.makeSuite(NeighbourTest)
	suite2 = unittest.makeSuite(EmptyGridTest)
	suite3 = unittest.makeSuite(SetValueTest)
	alltests = unittest.TestSuite((suite1,suite2,suite3))
	return alltests

if __name__ == "__main__":
	unittest.main()

