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
    if exists((position[0], position[1])) and \
       not is_empty((position[0], position[1]), B) and \
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
        if self.color == 'white':
            start_rank = 2
            move_fwd = 1
        if self.color == 'black':
            start_rank = 7
            move_fwd = -1
        if self.rank == start_rank and \
           is_empty((self.file, self.rank+move_fwd), B) and \
           is_empty((self.file, self.rank+(move_fwd*2)), B):
            possible_moves.append((self.file, self.rank+(move_fwd*2)))
        if is_empty((self.file, self.rank+move_fwd), B):
            possible_moves.append((self.file, self.rank+move_fwd))
        for pos in [(chr(ord(self.file)-1), self.rank+move_fwd), 
                    (chr(ord(self.file)+1), self.rank+move_fwd)]:
            if is_opponent(pos, B, self.color):
                possible_moves.append(pos)
        return possible_moves

class Rook(Piece):
    def get_moves(self, B):   
        possible_moves = []
        fwd_rng = zip([self.file]*8, range(self.rank+1, 9))
        bck_rng = zip([self.file]*8, range(self.rank-1, 0, -1))
        left_rng = zip(map(chr, range(ord(self.file)-1, 96, -1)), [self.rank]*8)
        right_rng = zip(map(chr, range(ord(self.file)+1, 105)), [self.rank]*8) 
        for rng in [fwd_rng, bck_rng, left_rng, right_rng]:
            for file, rank in rng: 
                if is_empty((file, rank), B):
                    possible_moves.append((file, rank))
                elif is_opponent((file, rank), B, self.color):
                    possible_moves.append((file, rank))
                    break
                else:
                    break  
        return possible_moves

class Knight(Piece):
    def get_moves(self, B):
        possible_moves = []
        # simply list all positions going clockwise from top right
        files = map(chr, [ord(self.file)+1, ord(self.file)+2, 
                          ord(self.file)+2, ord(self.file)+1, 
                          ord(self.file)-1, ord(self.file)-2,
                          ord(self.file)-2, ord(self.file)-1])
        ranks = [self.rank+2, self.rank+1, self.rank-1, self.rank-2,
                 self.rank-2, self.rank-1, self.rank+1, self.rank+2]
        for file, rank in zip(files, ranks):
            if is_empty((file, rank), B) or \
               is_opponent((file, rank), B, self.color):
               possible_moves.append((file, rank))
        return possible_moves

class Bishop(Piece):
    def get_moves(self, B):
        possible_moves = []
        top_right = zip(map(chr, range(ord(self.file)+1, 105)), 
                        range(self.rank+1, 9))
        btm_right = zip(map(chr, range(ord(self.file)+1, 105)), 
                        range(self.rank-1, 0, -1))
        btm_left = zip(map(chr, range(ord(self.file)-1, 96, -1)), 
                       range(self.rank-1, 0, -1))
        top_left = zip(map(chr, range(ord(self.file)-1, 96, -1)), 
                       range(self.rank+1, 9))
        for rng in [top_right, btm_right, btm_left, top_left]:
            for file, rank in rng:
                if is_empty((file, rank), B):
                    possible_moves.append((file, rank))
                elif is_opponent((file, rank), B, self.color):
                    possible_moves.append((file, rank))
                    break
                else:
                    break
        return possible_moves

class Queen(Piece):
    def get_moves(self, B):
        possible_moves = []
        fwd_rng = zip([self.file]*8, range(self.rank+1, 9))
        bck_rng = zip([self.file]*8, range(self.rank-1, 0, -1))
        left_rng = zip(map(chr, range(ord(self.file)-1, 96, -1)), [self.rank]*8)
        right_rng = zip(map(chr, range(ord(self.file)+1, 105)), [self.rank]*8)
        top_right = zip(map(chr, range(ord(self.file)+1, 105)), 
                        range(self.rank+1, 9))
        btm_right = zip(map(chr, range(ord(self.file)+1, 105)), 
                        range(self.rank-1, 0, -1))
        btm_left = zip(map(chr, range(ord(self.file)-1, 96, -1)), 
                       range(self.rank-1, 0, -1))
        top_left = zip(map(chr, range(ord(self.file)-1, 96, -1)), 
                       range(self.rank+1, 9))
        for rng in [fwd_rng, bck_rng, left_rng, right_rng,
                    top_right, btm_right, btm_left, top_left]:
            for file, rank in rng:
                if is_empty((file, rank), B):
                    possible_moves.append((file, rank))
                elif is_opponent((file, rank), B, self.color):
                    possible_moves.append((file, rank))
                    break
                else:
                    break
        return possible_moves

class King(Piece):
    def get_moves(self, B):
        possible_moves = []
        # starting from top right, going clockwise
        files = map(chr, [ord(self.file)+1, ord(self.file)+1, 
                          ord(self.file)+1, ord(self.file), 
                          ord(self.file)-1, ord(self.file)-1,
                          ord(self.file)-1, ord(self.file)])
        ranks = [self.rank+1, self.rank, self.rank-1, self.rank-1,
                 self.rank-1, self.rank, self.rank+1, self.rank+1]
        for file, rank in zip(files, ranks):
            if is_empty((file, rank), B) or \
               is_opponent((file, rank), B, self.color):
               # and not in_check((file, rank), B, self.color)
               possible_moves.append((file, rank))
        return possible_moves



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

        self.board['a'][1] = Rook('R', 'white', ('a', 1))
        self.board['h'][1] = Rook('R', 'white', ('h', 1))
        self.board['b'][1] = Knight('N', 'white', ('b', 1))
        self.board['g'][1] = Knight('N', 'white', ('g', 1))
        self.board['c'][1] = Bishop('B', 'white', ('c', 1))
        self.board['f'][1] = Bishop('B', 'white', ('f', 1))
        self.board['d'][1] = Queen('Q', 'white', ('d', 1))
        self.board['e'][1] = King('K', 'white', ('e', 1))

        self.board['a'][8] = Rook('r', 'black', ('a', 8))
        self.board['h'][8] = Rook('r', 'black', ('h', 8))
        self.board['b'][8] = Knight('n', 'black', ('b', 8))
        self.board['g'][8] = Knight('n', 'black', ('g', 8))
        self.board['c'][8] = Bishop('b', 'black', ('c', 8))
        self.board['f'][8] = Bishop('b', 'black', ('f', 8))
        self.board['d'][8] = Queen('q', 'black', ('d', 8))
        self.board['e'][8] = King('k', 'black', ('e', 8))

        for file in Board.files:
            self.board[file][2] = Pawn('P', 'white', (file, 2))
            self.board[file][7] = Pawn('p', 'black', (file, 7))

    def show(self):  # color arg could determine from who's perspective
        for rank in Board.ranks:
            print(str(rank), end=' ')
            for file in Board.files:
                if type(self.board[file][rank]) == str:   # empty square
                    print('['+self.board[file][rank]+']', end=' ')
                else:
                    print('['+self.board[file][rank].kind+']', end=' ')
            print('\n', end='')
        print('   a   b   c   d   e   f   g   h  ')

    def play(self):
        
        while True:
            self.show()

            piece = input('Which piece will you move? (ex. b2)\n')
            moves = self.board[piece[0]][int(piece[1])].get_moves(self)
            print('Where to? (enter a number)')
            for idx, move in enumerate(moves):
                print(idx, move)
            dest = input('')
            self.board[piece[0]][int(piece[1])].make_move(
                                moves[int(dest)], self)

        
b = Board()
b.play()

# print(b.board['a'][2].kind)
# print(b.board['a'][2].get_moves(b))


# b.board['e'][7] = Knight('N','white',('e',7))
# b.board['d'][6] = King('K','black',('d',6))
# b.show()
# print(b.board['d'][6].get_moves(b))




