#!/usr/bin/python
# Unit tests for board.py

import unittest
from board import *
from game import Player,Move

class BoardSizeTest(unittest.TestCase):
	'''Check that different sized boards can be created'''
	def testSquare(self):
		'''Check square boards between 2 and 50 work'''
		for i in range(3,51):
			theboard = RectangularBoard((i,i))
			self.assertTrue(theboard is not None)
			self.assertEquals(theboard.get_size(), (i,i))

	def testBadSize(self):
		'''Check that silly sized boards don't work'''
		for i in (-1,0,1,2):
			self.assertRaises(SizeError, RectangularBoard, (i,i))

	def testRectangular(self):
		'''Check a couple of rectangular boards'''
		for shape in ((9,13),(10,5),(21,6)):
			theboard = RectangularBoard(shape)
			self.assertTrue(theboard is not None)
			self.assertEquals(theboard.get_size(), shape)

class BoardTest(unittest.TestCase):
	def setUp(self):
		self.board = RectangularBoard((19,19))
		self.black = Player('black')
		self.white = Player('white')

class GroupTest(BoardTest):
	def testConnectedStones(self):
		'''Check connected stones are grouped together'''
		self.board.place_stone(Move((1,1),self.black))
		self.board.place_stone(Move((1,2),self.black))
		self.board.place_stone(Move((1,3),self.black))
		group1 = Group(self.board,(1,1))
		group2 = Group(self.board,(1,2))
		group3 = Group(self.board,(1,3))
		self.assertEquals(group1, group2, group3)
		self.assertTrue((1,1) in group1.stones)
		self.assertTrue((1,2) in group1.stones)
		self.assertTrue((1,3) in group1.stones)

	def testLibertiesCorner(self):
		'''Check the number of liberties of a group is correct for a corner group'''
		self.board.place_stone(Move((0,0),self.black))
		self.board.place_stone(Move((0,1),self.black))
		self.board.place_stone(Move((0,2),self.black))
		group1 = Group(self.board,(0,0))
		self.assertEquals(group1.liberties, 4)

	def testLibertiesSide(self):
		'''Check the number of liberties of a group is correct for a side group'''
		self.board.place_stone(Move((0,3),self.black))
		self.board.place_stone(Move((0,1),self.black))
		self.board.place_stone(Move((0,2),self.black))
		group1 = Group(self.board,(0,3))
		self.assertEquals(group1.liberties, 5)

	def testLibertiesCenter(self):
		'''Check the number of liberties of a group is correct for a center group'''
		self.board.place_stone(Move((2,4),self.black))
		self.board.place_stone(Move((2,2),self.black))
		self.board.place_stone(Move((2,3),self.black))
		group1 = Group(self.board,(2,4))
		self.assertEquals(group1.liberties, 8)

	def testLibertiesSurrounded(self):
		'''Check the number of liberties of a group is zero when surrounded'''
		self.board.place_stone(Move((0,0),self.black))
		self.board.place_stone(Move((0,1),self.black))
		self.board.place_stone(Move((0,2),self.black))
		self.board.place_stone(Move((0,3),self.white))
		self.board.place_stone(Move((1,0),self.white))
		self.board.place_stone(Move((1,1),self.white))
		self.board.place_stone(Move((1,2),self.white))
		group1 = Group(self.board,(0,0))
		self.assertEquals(group1.liberties, 0)

def suite():
	suite1 = unittest.makeSuite(BoardSizeTest)
	suite2 = unittest.makeSuite(GroupTest)
	alltests = unittest.TestSuite((suite1, suite2))
	return alltests

if __name__ == "__main__":
	unittest.main()
