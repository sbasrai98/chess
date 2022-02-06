import random
import copy
import time

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
        if self.kind == 'K' and self.color == 'white':
            B.king['white'] = destination
        if self.kind == 'k' and self.color == 'black':
            B.king['black'] = destination

    # will this move cause the player to be in check?
    # execute the move. find out answer. reverse the move and return answer
    def causes_check(self, destination, B):
        dest_file, dest_rank = destination
        og_dest_piece = B.board[dest_file][dest_rank]
        og_king = copy.deepcopy(B.king)
        og_captured = copy.deepcopy(B.captured)
        og_file = self.file
        og_rank = self.rank

        # test_board = copy.deepcopy(self) 
        # will still need to reverse self.rank/file changes

        self.make_move(destination, B)

        # now check if king is in check
        if self.color == 'white': opp_color = 'black'
        if self.color == 'black': opp_color = 'white'
        # get all opp_color pieces
        opp_pieces = B.get_pieces(opp_color)
        opp_moves = []
        for file, rank in opp_pieces:
            opp_moves.extend(B.board[file][rank].get_moves(B, check=False))
        if B.king[self.color] in opp_moves: 
            result = True
        else:
            result = False
        
        # now undo the move
        B.board[og_file][og_rank] = self
        self.file = og_file
        self.rank = og_rank
        B.board[dest_file][dest_rank] = og_dest_piece
        B.king = og_king
        B.captured = og_captured

        return result




class Pawn(Piece):
    def get_moves(self, B, check=True):  # pass Board object   
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
        if check: # remove any possible moves that put the king in check
            possible_moves = list(filter(
                lambda x: not(self.causes_check(x, B)), possible_moves))
        return possible_moves

class Rook(Piece):
    def get_moves(self, B, check=True):   
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
        if check: # remove any possible moves that put the king in check
            possible_moves = list(filter(
                lambda x: not(self.causes_check(x, B)), possible_moves)) 
        return possible_moves

class Knight(Piece):
    def get_moves(self, B, check=True):
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
        if check: # remove any possible moves that put the king in check
            possible_moves = list(filter(
                lambda x: not(self.causes_check(x, B)), possible_moves))
        return possible_moves

class Bishop(Piece):
    def get_moves(self, B, check=True):
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
        if check: # remove any possible moves that put the king in check
            possible_moves = list(filter(
                lambda x: not(self.causes_check(x, B)), possible_moves))
        return possible_moves

class Queen(Piece):
    def get_moves(self, B, check=True):
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
        if check: # remove any possible moves that put the king in check
            possible_moves = list(filter(
                lambda x: not(self.causes_check(x, B)), possible_moves))
        return possible_moves

class King(Piece):
    def get_moves(self, B, check=True):
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
        if check: # remove any possible moves that put the king in check
            possible_moves = list(filter(
                lambda x: not(self.causes_check(x, B)), possible_moves))
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

        first_rank = [Rook, Knight, Bishop, Queen, 
                      King, Bishop, Knight, Rook]
        letters = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for i in range(8):
            self.board[Board.files[i]][1] = first_rank[i](
                letters[i], 'white', (Board.files[i], 1))
            self.board[Board.files[i]][2] = Pawn(
                'P', 'white', (Board.files[i], 2))
            self.board[Board.files[i]][8] = first_rank[i](
                letters[i].lower(), 'black', (Board.files[i], 8))
            self.board[Board.files[i]][7] = Pawn(
                'p', 'black', (Board.files[i], 7))
        
        self.king = {'white':('e', 1), 'black':('e', 8)}
            
    def show(self):  # color arg could determine from who's perspective
        print('\n')
        print('captured:', 
              ''.join(map(lambda x: x.kind, self.captured['white'])))
        for rank in Board.ranks:
            print(str(rank), end=' ')
            for file in Board.files:
                if type(self.board[file][rank]) == str:   # empty square
                    print('['+self.board[file][rank]+']', end=' ')
                else:
                    print('['+self.board[file][rank].kind+']', end=' ')
            print('\n', end='')
        print('   a   b   c   d   e   f   g   h  ')
        print('captured:', 
              ''.join(map(lambda x: x.kind, self.captured['black'])))
        print('\n')

    def get_pieces(self, color):
        pieces = []
        for file in Board.files:
            for rank in Board.ranks:
                if not is_empty((file, rank), self) and \
                    self.board[file][rank].color == color:
                    pieces.append((file, rank))  
        return pieces

    def human_turn(self, color):
        if color == 'white': opp_color = 'Black'
        if color == 'black': opp_color = 'White'
        my_pieces = self.get_pieces(color)
        all_moves = []
        for file, rank in my_pieces:
            all_moves.extend(self.board[file][rank].get_moves(self))
        if all_moves == []:
            print(f'{opp_color} wins.')
            return True # game over
        piece = input('Which piece will you move?\n')
        while (piece[0], int(piece[1])) not in my_pieces:
            print(f'{piece} is not one of your pieces.')
            piece = input('Which piece will you move?\n')
        moves = self.board[piece[0]][int(piece[1])].get_moves(self)
        print('Where to?')
        for idx, move in enumerate(moves):
            print(f'{idx}: {move}')
        print('q: Go back')
        dest = input()
        while True: 
            if dest == 'q': 
                return self.human_turn(color)
            else:
                try:
                    p = type(self.board[piece[0]][int(piece[1])]).__name__
                    self.board[piece[0]][int(piece[1])].make_move(
                        moves[int(dest)], self)
                    loc = ''.join(map(str, moves[int(dest)]))
                    print(f'{color[0].upper() + color[1:]} \
moves {p} to {loc}.')
                    return False # game is not over
                except:
                    print('Not a valid option.')
                    dest = input('Where to?\n')
        
    def cpu_turn(self, color):
        if color == 'white': opp_color = 'Black'
        if color == 'black': opp_color = 'White'
        my_pieces = self.get_pieces(color)
        my_pieces = list(filter(
            lambda x: self.board[x[0]][x[1]].get_moves(self) != [],
            my_pieces))
        if my_pieces == []:
            print(f'{opp_color} wins.')
            return True # game over
        print(f'{color[0].upper() + color[1:]}\'s turn to move...')
        time.sleep(2)
        file, rank = random.choice(my_pieces)
        move_select = random.choice(
            self.board[file][rank].get_moves(self))

        p = type(self.board[file][rank]).__name__
        self.board[file][rank].make_move(move_select, self)
        
        loc = ''.join(map(str, move_select))
        print(f'{color[0].upper() + color[1:]} \
moves {p} to {loc}.')
        return False # game is not over
        
    def play(self, white='human', black='cpu'):        
        while True:
            self.show()
            if white == 'human':
                game_over = self.human_turn('white')
            else:
                game_over = self.cpu_turn('white')
            
            self.show() 
            if not game_over:
                if black == 'cpu':
                    game_over = self.cpu_turn('black')
                else:
                    game_over = self.human_turn('black')
            
            if game_over: break
    
b = Board()
b.play(white='human')
#print( type(b.board['a'][2]).__name__)

# b.board['c'][3] = Bishop('b', 'black', ('c', 3))
# b.board['d'][6] = King('K','black',('d',6))
# b.show()
# print(b.board['d'][6].get_moves(b))

# print(b.board['d'][2].get_moves(b))
# print(b.board['d'][2].causes_check(('d',3), b))

# b.show()




