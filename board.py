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

    def exists(self, position): 
        if position[0] in Board.files and position[1] in Board.ranks:
            return True
        return False

    def at(self, position):
        if self.board[position[0]][position[1]] != ' ':
            return self.board[position[0]][position[1]]
        return False 

    def set(self, position, piece):
        self.board[position[0]][position[1]] = piece

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
        opponent_color = 'black' if my_color == 'white' else 'white'
        opp_pieces = self.get_pieces(opponent_color)
        opp_moves = []
        for file, rank in opp_pieces:
            opp_moves.extend(self.at((file, rank)).get_moves(check=False))
        if position in opp_moves: 
            return True
        return False

    def move_piece(self, start, end, count):
        piece_captured = None
        first_rank = 1 if self.at(start).color == 'white' else 8
        if end[0] == 'q':   # queenside castle
            self.move_piece(('e', first_rank), ('c', first_rank), count)
            self.move_piece(('a', first_rank), ('d', first_rank), count)
        elif end[0] == 'k': # kingside castle
            self.move_piece(('e', first_rank), ('g', first_rank), count)
            self.move_piece(('h', first_rank), ('f', first_rank), count)
        elif end[1] == 'p': # en passant
            end_rank = 6 if self.at(start).color == 'white' else 3
            self.move_piece(start, (end[0], end_rank), count)
            killed = self.at((end[0], start[1]))
            self.captured[killed.color].append(killed)
            self.set((end[0], start[1]), ' ')
            return True
        elif type(end[1]) == str: # promotion. 8r, 8n, 8b, 8q
            l_rank = 8 if self.at(start).color == 'white' else 1
            piece_captured = self.move_piece(start, (end[0], l_rank), count)
            promo = dict(r=Rook, n=Knight, b=Bishop, q=Queen)
            color = self.at((end[0], l_rank)).color
            has_moved = self.at((end[0], l_rank)).has_moved
            kind = end[1][1] if color == 'black' else end[1][1].upper()
            self.set((end[0], l_rank), 
                promo[end[1][1]](kind, color, (end[0], l_rank), self, has_moved))
            return piece_captured
        else:               # normal move
            piece = self.at(start)
            piece.has_moved += count
            piece.file, piece.rank = end
            self.set(start, ' ')
            if self.at(end):
                self.captured[self.at(end).color].append(self.at(end))
                piece_captured = True
            self.set(end, piece)
            if type(self.at(end)) == King:
                self.king[self.at(end).color] = end
            return piece_captured      

    def make_move(self, start, end): 
        hist_entry = dict(piece=type(self.at(start)), 
            color=self.at(start).color, start=start, end=end, 
            capture=self.move_piece(start, end, 1))
        self.history.append(hist_entry)

    def reverse_move(self): # reverse the last move made using history
        prev = self.history.pop()
        first_rank = 1 if prev['color'] == 'white' else 8
        op_color = 'black' if prev['color'] == 'white' else 'white'
        if prev['end'][0] == 'q':     # queenside castle
            self.move_piece(('c', first_rank), ('e', first_rank), -1)
            self.move_piece(('d', first_rank), ('a', first_rank), -1)
        elif prev['end'][0] == 'k':   # kingside castle
            self.move_piece(('g', first_rank), ('e', first_rank), -1)
            self.move_piece(('f', first_rank), ('h', first_rank), -1)
        elif prev['end'][1] == 'p':   # en passant
            end_rank = 6 if prev['color'] == 'white' else 3
            self.move_piece((prev['end'][0], end_rank), prev['start'], -1)
            self.set((prev['end'][0], prev['start'][1]), 
                self.captured[op_color].pop())
        elif type(prev['end'][1]) == str:  # promotion. 8r, 8n, 8b, 8q
            l_rank = 8 if prev['color'] == 'white' else 1
            prev_file, prev_rank = prev['start'][0], prev['start'][1]
            kind = 'P' if prev['color'] == 'white' else 'p'
            self.move_piece((prev['end'][0], l_rank), prev['start'], -1)
            has_moved = self.at(prev['start']).has_moved
            if prev['capture']:
                self.set((prev['end'][0], l_rank), self.captured[op_color].pop())          
            self.set(prev['start'],
             Pawn(kind, prev['color'], (prev_file, prev_rank), self, has_moved))
        else:                         # normal move
            self.move_piece(prev['end'], prev['start'], -1)
            if prev['capture']:
                self.set(prev['end'], self.captured[op_color].pop())
        
    def causes_check(self, start, end):
        my_color = self.at(start).color
        self.make_move(start, end)
        # castling
        first_rank = 1 if my_color == 'white' else 8
        if end[0] == 'q':
            result = any([self.is_under_attack((x, first_rank), my_color) \
                for x in 'edc'])
        elif end[0] == 'k':
            result = any([self.is_under_attack((x, first_rank), my_color) \
                for x in 'ef'])
        else:   # normal move (or en passant or promotion)
            result = self.is_under_attack(self.king[my_color], my_color)
        self.reverse_move()
        return result

    def checkmate(self):
        my_color = self.history[-1]['color']
        my_color = my_color[0].upper()+my_color[1:]
        opp_color = 'black' if my_color == 'White' \
            else 'white'
        opp_pieces = self.get_pieces(opp_color)
        opp_moves = []
        for file, rank in opp_pieces:
            opp_moves.extend(self.at((file, rank)).get_moves())
        if opp_moves == []: return my_color
        return False

    def show(self):  # color arg could determine from who's perspective
        print('\ncaptured:', 
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
              ''.join(map(lambda x: x.kind, self.captured['black']))+'\n')
