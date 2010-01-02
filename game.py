from observer import Subject
import string
#Game of go

#game exceptions
class BoardError(Exception): pass
class SizeError(BoardError): pass

#invalid move exceptions
class InvalidMove(Exception): pass
class OccupiedError(InvalidMove): pass
class SuicideError(InvalidMove): pass
class KoError(InvalidMove): pass
class NonExistantSquareError(InvalidMove): pass

class AGARuleset:
        '''American go association rules'''
        nine_star_points = ((3,7),(7,3),(3,3),(7,7),(5,5)) #9x9
        thirteen_star_points = ((4,4), (9,9), (4,9), (9,4), (7,7),(4,7),(9,7),(7,4),(7,9)) #13x13
        nineteen_star_points = ((4,4),(16,16),(4,16),(16,5),(10,10),(4,10),(16,10),(10,4),(16,4)) #19x19

        def __init__(self):
                self.komi = 7

        def check_suicide(self,move,board):
		'''check to see if the stone has any liberties'''
		group = Group(board,move.position)
		if group.liberties == 0:
			raise SuicideError

	def check_superko(self,move,board,history):
		'''Check to see if the move resets the board to any of its previous states'''	
                if board in history:
                        raise KoError
                for i in history:
                        if i == board:
                                raise KoError

        def check_rules(self,move,board,history):
                testboard = board.__copy__()
		testboard.place_stone(move) #try the move
                testboard.remove_dead_stones(move) #remove stones it captures
                self.check_suicide(move,testboard) #check the stone is alive
                self.check_superko(move,testboard,history) #check it doesnt repeat a previous board position

        def game_over(self,history,white,black):
                '''game is over when black passes, then white passes'''
                pass

        def place_handicap(self,number,board,black):
                if boardsize == (9,9):
                        stars = AGARuleset.nine_star_points
                elif boardsize == (13,13):
                        stars = AGARuleset.thirteen_star_points
                elif boardsize == (19,19):
                        stars = AGARuleset.nineteen_star_points

                spaces = len(stars)
                if fixed_handicap > spaces:
                        fixed_handicap = spaces
                for i in range(fixed_handicap):
                        board.place_stone(stars[i],black)

                return spaces

class JapaneseScoring:
        def __init__(self):
                pass
        def score(self,board,dead_stone_positions,black,white,komi):
                for i in dead_stones:
                        group = Group(self,i)
                        if len(group.stones) > 0:
                                if group.owner == black:
                                        white.captures += len(group.stones)
                                else:
                                        black.captures += len(group.stones)
                                group.kill()
                score = self.territory(board,black,white)
                return (score[0]+black.captures,score[1]+white.captures+komi)

        def territory(board,black,white):
                pass


class TwoPlayerGame(Subject):
        '''Handles all the game logic for a 2 player game of go.'''

        def __init__(self,boardsize,fixed_handicap=0,komi=None,black='Black',white='White',custom_handicap=0,ruleset=None,scoring=None):
                Subject.__init__(self)
                self.board = Board(boardsize)

                if ruleset:
                        self.ruleset = ruleset
                else:
                        self.ruleset = AGARuleset()

                if scoring:
                        self.scoring = scoring
                else:
                        self.scoring = JapaneseScoring()

                self.history = [] # the board at all times in the past
                self.moves = [] #the list of moves
                self.black = Player('black',black)
                self.white = Player('white',white)
                self.winner = None

                if fixed_handicap or custom_handicap:
                        self.handicap = fixed_handicap + custom_handicap
                        if not komi:
                                komi = 0 #no komi on handicap games by default
                else:
                        self.handicap = 0

                if fixed_handicap:
                        placed_stones = ruleset.place_handicap(fixed_handicap,self.board,self.black)
                        if placed_stones < fixed_handicap:
                                custom_handicap += fixed_handicap - placed_stones

                if custom_handicap:
                        self.remaining_handicap = custom_handicap
                else:
                        self.remaining_handicap = 0

                #black goes first, unless they have a handicap
                if self.handicap and self.remaining_handicap == 0:
                        self.next_player = self.white
                else:
                        self.next_player = self.black

                #extra points to compensate white for black going first
                if komi:
                        self.komi = komi
                else:
                        self.komi = self.ruleset.komi

        def last_move(self):
                '''Return the last move played'''
                if self.moves:
                        return self.moves[-1]

        def change_player(self):
                '''Toggle the next player'''
                if self.next_player == self.black:
                        self.next_player = self.white
                else:
                        self.next_player = self.black
          
        def current_player(self):
                '''Return the id of the current player'''
                return self.next_player.color

        def last_move(self):
                if self.moves:
                        return self.moves[-1]

        def play_move(self,position,player):
                '''Play the next move'''
                if player is not self.next_player.color:
                        return

                move = Move(position,self.next_player)

                #check the move doesn't break the rules (will raise an exception if it does)
                self.ruleset.check_rules(move,self.board,self.history)

                #play the move
                self.board.place_stone(move)
                self.board.remove_dead_stones(move)
        
                #save the board state and move for later
                self.moves.append(move)
                self.history.append(self.board.__copy__())

                if not self.remaining_handicap:
                        self.change_player()
                else:
                        self.remaining_handicap -= 1

                self.notify()
				
        def pass_turn(self):
                '''Pass turn. If both players pass the game is over.'''
                self.moves.append(SpecialMove('pass',self.next_player))
                self.change_player()
                self.notify()

#                if self.moves and not self.remaining_handicap:
#                        if self.moves[-1].player == self.next_player: #the last player passed too
#                                self.japanese_scoring() #game over
#                        else:
#                                self.change_player()

        def resign(self):
                if self.next_player == self.black:
                        self.winner = self.white
                else:
                        self.winner = self.black

                self.notify()

        def game_over(self):
                return self.winner is not None
        
class Board(Subject):
	'''A rectangular board. Stones can be added to any square which isn't occupied.'''
	def __init__(self,size):
                Subject.__init__(self)
                if size[0] < 3 or size[1] < 3:
                        raise SizeError
		self.size = size
		self.squares = {}
		x=range(1,size[0]+1)
		y=range(1,size[1]+1)
		for i in x:
			for j in y:
				self.squares[(i,j)] = Square()

	def __eq__(self, other):
		'''Two boards are the same if all squares have the same state'''
		if self.squares == other.squares:
			return True
		return False

	def __copy__(self):
		'''Make a copy of this board.'''
		new_board = Board(self.size)
                for pos,square in self.squares.items():
                        if not square.empty():
                                new_board.squares[pos].place_stone(square.owner)
		return new_board

	def square(self,position):
		'''Return a certain square'''
		return self.squares[position]

	def place_stone(self,move):
                #check that there is a free space at that position
                self.check_free_space(move)

                #place the stone
                self.squares[move.position].place_stone(move.player)

                #notify observers
                self.notify()

        def check_free_space(self,move):
                '''Check to see if the space exists and is empty'''
                if move.position not in self.squares:
                        raise NonExistantSquareError

                if not self.square(move.position).empty():
                        raise OccupiedError

	def neighbours(self,position):
		'''Returns a list of positions of the neighbouring squares'''
		x = position[0]
		y = position[1]
		width = self.size[0]
		height = self.size[1]
		result = []
	
		if x > 1:
			result.append((x-1,y))
		if x < width:
			result.append((x+1,y))
		if y > 1:
			result.append((x,y-1))
		if y < height:
			result.append((x,y+1))

		return result

	def remove_dead_stones(self,move):
		'''Remove any stones which are captured by this move'''
		already_checked = []
		for position in self.neighbours(move.position):
			square = self.square(position)
			if (position not in already_checked) and (square.owner is not move.player):
				group = Group(self,position)
				already_checked.extend(group.stones) #save the positions of all the stones in this group to avoid checking the same group multiple times

				if group.liberties == 0: #the group is captured!
					move.player.captures += len(group.stones) #update the number of captured stones for this player
					group.kill() #remove the stones from the board
                self.notify() #notify observers


class Square:
	'''Responsible for the state of one square of the go board'''
	def __init__(self):
		self.owner = None

	def __eq__(self, other):
		return self.owner == other.owner

	def place_stone(self,player):
		self.owner = player

	def remove_stone(self):
		self.owner = None

	def empty(self):
		return self.owner == None

	def color(self):
		return self.owner.color

class Group:
	'''A group of stones which are connected '''
	def __init__(self,board,position):
		self.stones = [] #list of positions of the stones
		self.liberties = 0
		self.board = board
		start_point = board.square(position)
		if not start_point.empty():
			self.owner = start_point.owner
			self.stones.append(position)
			self.find_connected_stones(position)

        def __eq__(self,other):
                #check the size, liberties and board is the same
                if len(self.stones) is not len(other.stones) or self.owner is not other.owner or self.board is not other.board:
                        return False

                #check all the stones are the same
                for i in self.stones:
                        if i not in other.stones:
                                return False
                return True

	def find_connected_stones(self,position):
		'''Recursively add stones which are connected to the starting stone, and count the liberties of the group.'''
		neighbours = self.board.neighbours(position)
		for next in neighbours:
			if next not in self.stones:
				if self.board.square(next).empty():
					self.liberties += 1
				elif self.board.square(next).owner == self.owner:
					self.stones.append(next)
					self.find_connected_stones(next)

	def kill(self):
		for position in self.stones:
			square = self.board.square(position)
			square.remove_stone()

class Player:
	'''Stores information about a player'''
	def __init__(self,color,name=None):
                self.color = color
                if name:
                        self.name = name
                else:
			self.name = color
                self.captures = 0

class Move:
	'''Stores information about a move'''
	def __init__(self,position,player):
		self.position = position
		self.player = player

        def __str__(self):
                d = int(self.position[0]-1)
                letters = [l for l in string.ascii_uppercase if l is not 'I']
                x = letters[d]
                y = self.position[1]
                return '%s %s%d'%(self.player.color,x,y)

class SpecialMove:
        def __init__(self,type,player):
                self.type = type
                self.player = player

        def __str__(self):
                return '%s %s'%(self.player.color,self.type)
