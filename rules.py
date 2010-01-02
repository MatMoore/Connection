from copy import copy

#invalid move exceptions
class InvalidMove(Exception): pass
class OccupiedError(InvalidMove): pass
class SuicideError(InvalidMove): pass
class KoError(InvalidMove): pass
class NonExistantSquareError(InvalidMove): pass

nine_star_points = ((3,7),(7,3),(3,3),(7,7),(5,5)) #9x9
thirteen_star_points = ((4,4), (9,9), (4,9), (9,4), (7,7),(4,7),(9,7),(7,4),(7,9)) #13x13
nineteen_star_points = ((4,4),(16,16),(4,16),(16,5),(10,10),(4,10),(16,10),(10,4),(16,4)) #19x19

class AGARules:
        '''American go association rules'''
        #check if a move on the board
        def check_suicide(self,move,board):
        '''check to see if the stone has any liberties'''
        group = board.group(move.position)
        if group.liberties == 0:
            raise SuicideError

        def check_ko(self,move,board,history):
            '''Check to see if the move resets the board to any of its previous states'''
            if board in history:
                raise KoError

        def check_rules(self,move,board,history):
            testboard = copy(board)
            testboard.place_stone(move) #try the move
            testboard.remove_dead_stones(move) #remove stones it captures
            self.check_suicide(move,testboard) #check the stone is alive
            self.check_superko(move,testboard,history) #check it doesnt repeat a previous board position

        def game_over(self,history,white,black):
                '''game is over when black passes, then white passes'''
                pass

        def score(self, board, dead_stone_positions, black, white, komi):
            return score_japanese(board,dead_stone_positions,black,white,komi)

#        def place_handicap(self,number,board,black):
#                if boardsize == (9,9):
#                        stars = AGARuleset.nine_star_points
#                elif boardsize == (13,13):
#                        stars = AGARuleset.thirteen_star_points
#                elif boardsize == (19,19):
#                        stars = AGARuleset.nineteen_star_points

#                spaces = len(stars)
#                if fixed_handicap > spaces:
#                        fixed_handicap = spaces
#                for i in range(fixed_handicap):
#                        board.place_stone(stars[i],black)
#
#                return spaces

#rewrite this
def score_japanese(board,dead_stone_positions,black,white,komi):
    for i in dead_stones:
        group = Group(self,i)
        if len(group.stones) > 0:
            if group.owner == black:
                white.captures += len(group.stones)
            else:
                black.captures += len(group.stones)
            group.kill()
            score = board.territory()
            return (score[0]+black.captures,score[1]+white.captures+komi)
