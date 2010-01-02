#unit test for game.py

from game import *
#from display import *
import unittest

class BoardSizeTest(unittest.TestCase):
    '''Check that different sized boards can be created'''
    def testSquare(self):
        '''Check square boards between 2 and 50 work'''
        for i in range(3,51):
            theboard = Board((i,i))
            assert theboard is not None
            assert theboard.size == (i,i)

    def testBadSize(self):
        '''Check that silly sized boards don't work'''
        for i in (-1,0,1,2):
            self.assertRaises(SizeError, Board, (i,i))

    def testRectangular(self):
        '''Check a couple of rectangular boards'''
        for shape in ((9,13),(10,5),(21,6)):
            theboard = Board(shape)
            assert theboard is not None
            assert theboard.size == shape

class BoardTest(unittest.TestCase):
    def setUp(self):
        self.board = Board((19,19))
        self.black = Player('black')
        self.white = Player('white')

class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = TwoPlayerGame((19,19))

class GroupTest(BoardTest):
    def testConnectedStones(self):
        '''Check connected stones are grouped together'''
        self.board.place_stone(Move((1,1),self.black))
        self.board.place_stone(Move((1,2),self.black))
        self.board.place_stone(Move((1,3),self.black))
        group1 = Group(self.board,(1,1))
        group2 = Group(self.board,(1,2))
        group3 = Group(self.board,(1,3))
        assert group1 == group2 == group3
        assert (1,1) in group1.stones
        assert (1,2) in group1.stones
        assert (1,3) in group1.stones

    def testLibertiesCorner(self):
        '''Check the number of liberties of a group is correct for a corner group'''
        self.board.place_stone(Move((1,1),self.black))
        self.board.place_stone(Move((1,2),self.black))
        self.board.place_stone(Move((1,3),self.black))
        group1 = Group(self.board,(1,1))
        assert group1.liberties == 4

    def testLibertiesSide(self):
        '''Check the number of liberties of a group is correct for a side group'''
        self.board.place_stone(Move((1,4),self.black))
        self.board.place_stone(Move((1,2),self.black))
        self.board.place_stone(Move((1,3),self.black))
        group1 = Group(self.board,(1,4))
        assert group1.liberties == 5

    def testLibertiesCenter(self):
        '''Check the number of liberties of a group is correct for a center group'''
        self.board.place_stone(Move((2,4),self.black))
        self.board.place_stone(Move((2,2),self.black))
        self.board.place_stone(Move((2,3),self.black))
        group1 = Group(self.board,(2,4))
        assert group1.liberties == 8

    def testLibertiesSurrounded(self):
        '''Check the number of liberties of a group is zero when surrounded'''
        self.board.place_stone(Move((1,1),self.black))
        self.board.place_stone(Move((1,2),self.black))
        self.board.place_stone(Move((1,3),self.black))
        self.board.place_stone(Move((1,4),self.white))
        self.board.place_stone(Move((2,1),self.white))
        self.board.place_stone(Move((2,2),self.white))
        self.board.place_stone(Move((2,3),self.white))
        group1 = Group(self.board,(1,1))
        assert group1.liberties == 0

class MoveTest(GameTest):
    def testBadMovePositions(self):
        '''Check that moves played outside the board don't work'''
        for position in ((-1,-1),(1,0),(2,20)):
            self.assertRaises(NonExistantSquareError,self.game.play_move,position)

    def testValidMove(self):
        '''Check that the square is occupied by a stone after the move'''
        self.game.play_move((1,1))
        topleft = self.game.board.square((1,1))
        assert topleft is not None
        assert not topleft.empty()
        assert topleft.owner == self.game.black

    def testOccupiedSquare(self):
        '''Check that the stone is not placed if the square is already occupied'''
        move1 = (1,1)
        self.game.play_move(move1)
        move2 = move1
        self.assertRaises(OccupiedError, self.game.play_move, move2)

    def testCapture(self):
        '''Check a captured stone is removed'''
        move1 = (1,1)
        move2 = (2,1)
        move3 = (5,5)
        capture = (1,2)
        self.game.play_move(move1)
        self.game.play_move(move2)
        self.game.play_move(move3)
        self.game.play_move(capture)

        topleft = self.game.board.square((1,1))
        assert topleft.empty()

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
    suite1 = unittest.makeSuite(BoardSizeTest)
    suite2 = unittest.makeSuite(MoveTest)
    suite3 = unittest.makeSuite(GroupTest)
    alltests = unittest.TestSuite((suite1, suite2,suite3))
    return alltests

if __name__ == "__main__":
    unittest.main() 

#class TextDisplayTester:
#	def __init__(self):
#		self.board = Board((19,19))
#		self.black = Player('black')
#		self.white = Player('white')
#		self.renderer = TextDisplay(self.board)
#	def draw(self):
#		self.renderer.draw()
#
#test1 = TextDisplayTester()
#test1.board.place_stone(Move((1,1),test1.black))
#test1.draw()


