from copy import copy,deepcopy

class Board(Observable):
    '''A rectangular board. Stones can be added to any square which isnt occupied.'''

    def __init__(self,grid):
        Observable.__init__(self)
        self.grid = grid

    def __eq__(self, other):
        '''Two boards are the same if all squares have the same state'''
        return self.grid == other.grid

    def __copy__(self):
        '''Make a copy of this board.'''
        return Board(deepcopy(self.grid))

    def points(self):
        for i in self.grid.points:
            yield i

    def connections(self):
        for i in self.grid.connections:
            yield i

    def place_stone(self, pos):
        #check that there is a free space at that position
        self.check_free_space(move)

        #place the stone
        self.squares[move.position].place_stone(move.player)

    def check_free_space(self,move):
        '''Check to see if the space exists and is empty'''
        if move.position not in self.squares:
            raise NonExistantSquareError

        if not self.square(move.position).empty():
            raise OccupiedError

    def remove_stone(self, pos):
        self.grid.set_point(pos[0], pos[1], None)

    def get_point(self, pos):
        return self.grid.get_point(pos[0], pos[1])

    def is_empty(self, pos):
        return (self.get_point(pos) is None)

    def neighbours(self,pos):
        '''Returns a list of positions of the neighbouring squares'''
        return self.grid.neighbours(pos[0], pos[1])

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

    def group(self,pos):
        return Group(self,pos)

class Group:
    '''A group of stones which are connected '''
    def __init__(self,board,position):
        self.stones = [] #list of positions of the stones
        self.liberties = 0
        self.board = board
        start_point = board.get_point(position[0]. position[1])
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
                if self.board.is_empty(next):
                    self.liberties += 1
                elif self.board.get_point(next) is self.owner:
                    self.stones.append(next)
                    self.find_connected_stones(next)

    def kill(self):
        for position in self.stones:
            self.board.remove_stone(position)
