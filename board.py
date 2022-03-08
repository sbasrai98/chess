import time
from copy import deepcopy, copy
from pieces import *

class Board:
    files = ['a','b','c','d','e','f','g','h']  # column names
    ranks = list(range(8,0,-1))                # row names

    def __init__(self):
        self.board = dict.fromkeys(Board.files)
        for k in list(self.board):
            rank = dict.fromkeys(Board.ranks)
            for pos in rank:
                rank[pos] = ' '
            self.board[k] = rank
        self.history = []
        self.captured = {'white':[], 'black':[]}
        self.king = {'white':('e', 1), 'black':('e', 8)}
        first_rank = [Rook, Knight, Bishop, Queen, 
                      King, Bishop, Knight, Rook]
        letters = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for i in range(8):
            self.board[Board.files[i]][1] = first_rank[i](
                letters[i], 'white', (Board.files[i], 1), self)
            self.board[Board.files[i]][2] = Pawn(
                'P', 'white', (Board.files[i], 2), self)
            self.board[Board.files[i]][8] = first_rank[i](
                letters[i].lower(), 'black', (Board.files[i], 8), self)
            self.board[Board.files[i]][7] = Pawn(
                'p', 'black', (Board.files[i], 7), self)

    def at(self, position):
        if self.board[position[0]][position[1]] != ' ':
            return self.board[position[0]][position[1]]
        return False 

    def exists(self, position): 
        if position[0] in Board.files and position[1] in Board.ranks:
            return True
        return False

    def is_empty(self, position):
        if self.exists(position) and not(self.at(position)):
            return True
        return False

    def is_opponent(self, position, my_color):
        opponent_color = 'black' if my_color == 'white' else 'white'
        if self.exists(position) and \
            not self.is_empty(position) and \
            self.at(position).color == opponent_color:
            return True
        return False

    def get_pieces(self, color):
        pieces = []
        for file in Board.files:
            for rank in Board.ranks:
                if not self.is_empty((file, rank)) and \
                    self.at((file, rank)).color == color:
                    pieces.append((file, rank))  
        return pieces

    def is_under_attack(self, position, my_color):
        #start_time = time.time()
        
        
        opponent_color = 'black' if my_color == 'white' else 'white'
        opp_pieces = self.get_pieces(opponent_color)
        opp_moves = []
        for file, rank in opp_pieces:
            opp_moves.extend(self.at((file, rank)).get_moves(check=False))
        if position in opp_moves: 
            result = True
        else:
            result = False
        #print("%s seconds for is_under_attack to run" % (time.time() - start_time))
        return result

    def move_piece(self, start, end):
        og_board = deepcopy(self.board)
        og_piece = deepcopy(self.at(start))

        first_rank = 1 if self.at(start).color == 'white' else 8
        if end[0] == 'q':   # queenside castle
            self.move_piece(('e', first_rank), ('c', first_rank))
            self.move_piece(('a', first_rank), ('d', first_rank))
        elif end[0] == 'k': # kingside castle
            self.move_piece(('e', first_rank), ('g', first_rank))
            self.move_piece(('h', first_rank), ('f', first_rank))
        elif end[1] == 'p': # en passant
            end_rank = 6 if self.at(start).color == 'white' else 3
            self.move_piece(start, (end[0], end_rank))
            killed = self.at((end[0], start[1]))
            self.captured[killed.color].append(killed)
            self.board[end[0]][start[1]] = ' '
        else:               # normal move
            piece = self.at(start)
            piece.has_moved += 1
            piece.file, piece.rank = end
            self.board[start[0]][start[1]] = ' '
            if self.at(end):
                self.captured[self.at(end).color].append(self.at(end))
            self.board[end[0]][end[1]] = piece
            if type(self.at(end)) == King:
                self.king[self.at(end).color] = end

            # pawn promotions...        

        hist_entry = dict(board=og_board, piece=og_piece,
                          start=start, end=end) # could add killed too..
        self.history.append(hist_entry)

    def causes_check(self, start, end):
        #start_time = time.time()

        my_color = self.at(start).color
        opp_color = 'black' if my_color == 'white' else 'white'
        test = Board()
        #strt2 = time.time()
        test.board, test.king = deepcopy(self.board), deepcopy(self.king)
        #print("%s seconds for deepcopies to run" % (time.time() - strt2))
        test.move_piece(start, end)
        # castling
        first_rank = 1 if my_color == 'white' else 8
        if end[0] == 'q':
            result = any([test.is_under_attack((x, first_rank), my_color) \
                for x in ['e','d','c']])
        elif end[0] == 'k':
            result = any([test.is_under_attack((x, first_rank), my_color) \
                for x in ['e','f']])
        else:
            # normal move (or en passant)
            result = test.is_under_attack(test.king[my_color], my_color)

        #print("%s seconds for causes_check to run" % (time.time() - start_time))
        return result

    def show(self):  # color arg could determine from who's perspective
        print('\n')
        print('captured:', 
              ''.join(map(lambda x: x.kind, self.captured['white'])))
        for rank in Board.ranks:
            print(str(rank), end=' ')
            for file in Board.files:
                if type(self.board[file][rank]) == str:   # empty square
                    print('['+self.board[file][rank]+']', end='')
                else:
                    print('['+self.board[file][rank].kind+']', end='')
            print('\n', end='')
        print('   a  b  c  d  e  f  g  h ')
        print('captured:', 
              ''.join(map(lambda x: x.kind, self.captured['black'])))
        print('\n')


if __name__ == '__main__':
    b = Board()
    b.board['b'][2] = Pawn('P', 'white', ('b',2), b)
    b.board['c'][3] = Pawn('p', 'black', ('c',3), b)
    b.show()
    print(b.board['b'][2].get_moves())
    print(type(b.board['b'][2]))