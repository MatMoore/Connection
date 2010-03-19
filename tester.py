#!/usr/bin/python
# Unit tests for game.py

from game import *
from board import *
import unittest

class GameTest(unittest.TestCase):
	def setUp(self):
		board = RectangularBoard((19,19))
		self.game = TwoPlayerGame(board)

class MoveTest(GameTest):
	def testBadMovePositions(self):
		'''Check that moves played outside the board don't work'''
		for position in ((-1,-1),(2,20)):
			self.assertRaises(NonExistantPointError,self.game.play_move,position,self.game.black)

	def testValidMove(self):
		'''Check that the square is occupied by a stone after the move'''
		self.game.play_move((0,0),self.game.black)
		topleft = self.game.board.get_point((0,0))
		self.assertTrue(topleft is not None)
		self.assertEquals(topleft, self.game.black)

	def testOccupiedSquare(self):
		'''Check that the stone is not placed if the square is already occupied'''
		move1 = ((1,1))
		self.game.play_move(move1,self.game.black)
		self.assertRaises(OccupiedError, self.game.play_move, move1, self.game.white)

	def testCapture(self):
		'''Check a captured stone is removed'''
		move1 = (0,0)
		move2 = (1,0)
		move3 = (4,4)
		capture = (0,1)
		self.game.play_move(move1,self.game.black)
		self.game.play_move(move2,self.game.white)
		self.game.play_move(move3,self.game.black)
		self.game.play_move(capture,self.game.white)

		topleft = self.game.board.get_point((0,0))
		self.assertTrue(topleft is None)

	def testKoViolated(self):
		'''Check that we cannot retake the ko without the board changing'''
		move1 = (2,1) #black
		move2 = (2,2) #white
		move3 = (1,2) #black
		move4 = (1,3) #white
		move5 = (5,5) #black
		move6 = (1,1) #white captures
		violatesKo = (1,2) #black
		self.game.play_move(move1)
		self.game.play_move(move2)
		self.game.play_move(move3)
		self.game.play_move(move4)
		self.game.play_move(move5)
		self.game.play_move(move6)
		self.assertRaises(KoError, self.game.play_move, violatesKo)

	def testTakeKo(self):
		'''Check that if the board changes, we can retake the ko'''
		move1 = (2,1) #black
		move2 = (2,2) #white
		move3 = (1,2) #black
		move4 = (1,3) #white
		move5 = (5,5) #black
		move6 = (1,1) #white captures
		move7 = (10,10) #black
		move8 = (11,11) #white
		legal = (1,2) #black
		self.game.play_move(move1)
		self.game.play_move(move2)
		self.game.play_move(move3)
		self.game.play_move(move4)
		self.game.play_move(move5)
		self.game.play_move(move6)
		self.game.play_move(move7)
		self.game.play_move(move8)
		self.game.play_move(legal)

	def testSuicideForbidden(self):
		'''Check for suicide'''
		move1 = (2,1) #white
		move2 = (5,5) #black
		move3 = (1,2) #white
		suicide = (1,1) #black
		self.game.play_move(move1)
		self.game.play_move(move2)
		self.game.play_move(move3)
		self.assertRaises(SuicideError, self.game.play_move, suicide)

	def testCapturingNotSuicide(self):
		'''Check that placing a stone with no liberties is ok if it captures a group'''
		move1 = (2,1) #white
		move2 = (2,2) #black
		move3 = (1,2) #white
		move4 = (1,3) #black
		move5 = (5,5) #white
		notSuicide = (1,1) #black

		self.game.play_move(move1)
		self.game.play_move(move2)
		self.game.play_move(move3)
		self.game.play_move(move4)
		self.game.play_move(move5)
		self.game.play_move(notSuicide)

def suite():
	suite1 = unittest.makeSuite(MoveTest)
	alltests = unittest.TestSuite((suite1))
	return alltests

if __name__ == "__main__":
	unittest.main()
