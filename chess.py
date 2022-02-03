def exists(position):  # (file, rank) tuple
    if position[0] in ['a','b','c','d','e','f','g','h'] and \
       position[1] in list(range(8,0,-1)):
        return True
    else:
        return False

def is_empty(position, B):
    if exists(position) and B.board[position[0]][position[1]] == ' ':
        return True
    else:
        return False

def is_opponent(position, B, my_color):
    if my_color == 'white': opponent_color = 'black'
    if my_color == 'black': opponent_color = 'white'
    if not is_empty((position[0], position[1]), B) and \
       B.board[position[0]][position[1]].color == opponent_color:
        return True
    else:
        return False

class Piece:
    def __init__(self, kind, color, position):
        self.kind = kind
        self.color = color
        self.file = position[0] 
        self.rank = position[1]
        
    def make_move(self, destination, B):
        B.board[self.file][self.rank] = ' '
        if not is_empty((destination[0], destination[1]), B):
            cap_color = B.board[destination[0]][destination[1]].color 
            B.captured[cap_color].append(B.board[destination[0]][destination[1]])
        B.board[destination[0]][destination[1]] = self
        self.file = destination[0]
        self.rank = destination[1]
            

class Pawn(Piece):
    def get_moves(self, B):  # pass Board object   
        possible_moves = []
        if self.rank == 2 and is_empty((self.file, self.rank+1), B) and \
           is_empty((self.file, self.rank+2), B):
            possible_moves.append((self.file, self.rank+2))
        if is_empty((self.file, self.rank+1), B):
            possible_moves.append((self.file, self.rank+1))
        for pos in [(chr(ord(self.file)-1), self.rank+1), 
                    (chr(ord(self.file)+1), self.rank+1)]:
            if exists(pos) and is_opponent(pos, B, self.color):
                possible_moves.append(pos)
        return possible_moves

class Rook(Piece):
    def get_moves(self, B):   
        possible_moves = []
        

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
        
        self.captured = {'white':[], 'black':[]}

        white_rank_1 = list('RNBQKBNR')
        for file, piece in zip(Board.files, white_rank_1):
            self.board[file][1] = Piece(piece, 'white', (file, 1)) 
            self.board[file][2] = Pawn('P', 'white', (file, 2))

    def show(self):  # color arg will determine from who's perspective
        for rank in Board.ranks:
            print(str(rank), end=' ')
            for file in Board.files:
                if type(self.board[file][rank]) == str:   # empty square
                    print('['+self.board[file][rank]+']', end=' ')
                else:
                    print('['+self.board[file][rank].kind+']', end=' ')
            print('\n', end='')
        print('   a   b   c   d   e   f   g   h  ')
        
b = Board()
b.show()

print(b.board['a'][2].kind)
print(b.board['a'][2].get_moves(b))

# put a piece on a4
#b.board['a'][4] = Piece('Q','black',('a',4))
#print(b.board['a'][2].get_moves(b.board))


b.board['b'][3] = Piece('Q','black',('b',3))
b.board['d'][3] = Piece('Q','black',('d',3))
b.show()
print(b.board['c'][2].get_moves(b))

b.board['c'][2].make_move(('b',3), b)
b.show()
print(b.board['b'][3].get_moves(b))
print(b.captured)

