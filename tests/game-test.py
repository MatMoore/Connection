#!/usr/bin/python
# Unit tests for game.py

from game import *
from board import *
from rules import *
from gameErrors import *
import unittest
import player

class GameTest(unittest.TestCase):
	def setUp(self):
		board = RectangularBoard((19,19))
		self.game = TwoPlayerGame(board)
		self.black, self.white = self.game.players

class MoveTest(GameTest):
	def testBadMovePositions(self):
		'''Check that moves played outside the board don't work'''
		for position in ((-1,-1),(2,20)):
			self.assertRaises(InvalidMove,self.game.play_move,position,self.black)

	def testValidMove(self):
		'''Check that the square is occupied by a stone after the move'''
		topleft = self.game.board.get_point((0,0))
		self.assertTrue(topleft is None)
		self.game.play_move((0,0),self.black)
		topleft = self.game.board.get_point((0,0))
		self.assertTrue(topleft is not None)
		self.assertEquals(topleft, (self.black,STONE))

	def testOccupiedSquare(self):
		'''Check that the stone is not placed if the square is already occupied'''
		move1 = (1,1)
		self.game.play_move(move1,self.black)
		self.assertRaises(InvalidMove, self.game.play_move, move1, self.white)

	def testCapture(self):
		'''Check a captured stone is removed'''
		move1 = (0,0)
		move2 = (1,0)
		move3 = (4,4)
		capture = (0,1)
		self.game.play_move(move1,self.black)
		self.game.play_move(move2,self.white)
		self.game.play_move(move3,self.black)
		self.game.play_move(capture,self.white)

		topleft = self.game.board.get_point((0,0))
		self.assertTrue(topleft is None)

	def testKoViolated(self):
		'''Check that we cannot retake the ko without the board changing'''
		move1 = (1,0) #black
		move2 = (1,1) #white
		move3 = (0,1) #black
		move4 = (0,2) #white
		move5 = (4,4) #black
		move6 = (0,0) #white captures
		violatesKo = (0,1) #black
		self.game.play_move(move1,self.black)
		self.game.play_move(move2,self.white)
		self.game.play_move(move3,self.black)
		self.game.play_move(move4,self.white)
		self.game.play_move(move5,self.black)
		self.game.play_move(move6,self.white)
		self.assertRaises(InvalidMove, self.game.play_move, violatesKo,self.black)

	def testTakeKo(self):
		'''Check that if the board changes, we can retake the ko'''
		move1 = (1,0) #black
		move2 = (1,1) #white
		move3 = (0,1) #black
		move4 = (0,2) #white
		move5 = (4,4) #black
		move6 = (0,0) #white captures
		move7 = (9,9) #black
		move8 = (10,10) #white
		legal = (0,1) #black
		self.game.play_move(move1,self.black)
		self.game.play_move(move2,self.white)
		self.game.play_move(move3,self.black)
		self.game.play_move(move4,self.white)
		self.game.play_move(move5,self.black)
		self.game.play_move(move6,self.white)
		self.game.play_move(move7,self.black)
		self.game.play_move(move8,self.white)
		self.game.play_move(legal,self.black)

	def testSuicideForbidden(self):
		'''Check for suicide'''
		move1 = (1,0) #white
		move2 = (4,4) #black
		move3 = (0,1) #white
		suicide = (0,0) #black
		self.game.play_move(move1,self.black)
		self.game.play_move(move2,self.white)
		self.game.play_move(move3,self.black)
		self.assertRaises(InvalidMove, self.game.play_move, suicide,self.white)

	def testCapturingNotSuicide(self):
		'''Check that placing a stone with no liberties is ok if it captures a group'''
		move1 = (1,0) #white
		move2 = (1,1) #black
		move3 = (0,1) #white
		move4 = (0,2) #black
		move5 = (4,4) #white
		notSuicide = (0,0) #black

		self.game.play_move(move1,self.black)
		self.game.play_move(move2,self.white)
		self.game.play_move(move3,self.black)
		self.game.play_move(move4,self.white)
		self.game.play_move(move5,self.black)
		self.game.play_move(notSuicide,self.white)

def suite():
	suite1 = unittest.makeSuite(MoveTest)
	alltests = unittest.TestSuite((suite1))
	return alltests

if __name__ == "__main__":
	unittest.main()
