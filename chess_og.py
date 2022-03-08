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

def under_attack(position, B, my_color):
    if my_color == 'white': opponent_color = 'black'
    if my_color == 'black': opponent_color = 'white'
    opp_pieces = B.get_pieces(opponent_color)
    opp_moves = []
    for file, rank in opp_pieces:
        opp_moves.extend(B.board[file][rank].get_moves(B, check=False))
    if position in opp_moves: 
        result = True
    else:
        result = False

class Piece:
    def __init__(self, kind, color, position):
        self.kind = kind
        self.color = color
        self.file = position[0] 
        self.rank = position[1]
        
    def make_move(self, destination, B, player='cpu'):
        ### CASTLING ###
        if self.color == 'white': rook_rank = 1
        if self.color == 'black': rook_rank = 8
        if destination[0] == 'q':
            B.board['e'][rook_rank].make_move(('c', rook_rank), B)
            B.board['a'][rook_rank].make_move(('d', rook_rank), B)
        elif destination[0] == 'k':
            
            B.board['e'][rook_rank].make_move(('g', rook_rank), B)
            B.board['h'][rook_rank].make_move(('f', rook_rank), B)
            
            #print(self.kind, self.color, self.file, self.rank)
        else:
            # normal move
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

            # pawn promotions. if player is set to human, ask for input()
            options = zip([Queen, Bishop, Rook, Knight], ['Q','B','R','N'])
            new_piece = random.choice(
                [piece(k, 'white', destination) for piece, k in options])
            if self.kind == 'P' and self.color == 'white' and \
                self.rank == 8:
                B.board[destination[0]][destination[1]] = new_piece
            if self.kind == 'p' and self.color == 'black' and \
                self.rank == 1:
                new_piece.kind, new_piece.color = new_piece.kind.lower(), 'black'
                B.board[destination[0]][destination[1]] = new_piece


    # will this move cause the player to be in check?
    # execute the move. find out answer. reverse the move and return answer
    def causes_check(self, destination, B):
        if self.color == 'white': rook_rank = 1
        if self.color == 'black': rook_rank = 8
        dest_file, dest_rank = destination
        if dest_file not in ('q', 'k'):
            og_dest_piece = B.board[dest_file][dest_rank]
        og_king = copy.deepcopy(B.king)
        og_captured = copy.deepcopy(B.captured)
        og_file = self.file
        og_rank = self.rank

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
        elif dest_file == 'q' and \
            (('d', rook_rank) in opp_moves or ('e', rook_rank) in opp_moves):
            result = True
        elif dest_file == 'k' and \
            (('f', rook_rank) in opp_moves or ('e', rook_rank) in opp_moves): 
            result = True
        else:
            result = False
        
        # now undo the move
        B.board[og_file][og_rank] = self
        self.file = og_file
        self.rank = og_rank
        if dest_file == 'q':
            B.board['a'][rook_rank] = B.board['d'][rook_rank]
            B.board['a'][rook_rank].file = 'a' # the rank wouldn't have changed.
            B.board['d'][rook_rank] = ' '
            B.board['c'][rook_rank] = ' '
        elif dest_file == 'k':
            B.board['h'][rook_rank] = B.board['f'][rook_rank]
            B.board['h'][rook_rank].file = 'h' # the rank wouldn't have changed.
            B.board['f'][rook_rank] = ' '
            B.board['g'][rook_rank] = ' '
        else:
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

        # castling
        king_moved = list(filter(
            lambda x: x['piece'].kind == self.kind, B.history))
        if self.color == 'white': rook_rank = 1
        if self.color == 'black': rook_rank = 8
        q_rook_moved = len(list(filter(
            lambda x: type(x['piece']) == Rook and \
                      x['piece'].color == self.color and \
                      x['piece'].file == 'a' and \
                      x['piece'].rank == rook_rank, B.history)))
        k_rook_moved = len(list(filter(
            lambda x: type(x['piece']) == Rook and \
                      x['piece'].color == self.color and \
                      x['piece'].file == 'h' and \
                      x['piece'].rank == rook_rank, B.history)))
        q_side_full = len(list(filter(lambda x: not(is_empty(x, B)), 
                           [(r, rook_rank) for r in ['b','c','d']])))
        k_side_full = not(is_empty(('f', rook_rank), B) and \
                          is_empty(('g', rook_rank), B))
        if not(king_moved) and not(q_rook_moved) and not(q_side_full):
            possible_moves.append(('q', 0))
        if not(king_moved) and not(k_rook_moved) and not(k_side_full):
            possible_moves.append(('k', 0))

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
        self.history = []
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
            return False # game does not continue.
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
                    turn_record = {'board': copy.deepcopy(self.board), # before the move is made
                                'piece': copy.deepcopy(self.board[file][rank]),
                                'dest': moves[int(dest)]} 
                    p = type(self.board[piece[0]][int(piece[1])]).__name__
                    self.board[piece[0]][int(piece[1])].make_move(
                        moves[int(dest)], self)
                    loc = ''.join(map(str, moves[int(dest)]))
                    print(f'{color[0].upper() + color[1:]} \
moves {p} to {loc}.')
                    self.history.append(turn_record)
                    return (piece[0], piece[1], 
                        moves[int(dest)][0], moves[int(dest)][1]) # game continues
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
            #print(f'{opp_color} wins.')
            return False # game does not continue.
        #print(f'{color[0].upper() + color[1:]}\'s turn to move...')
        #time.sleep(1)

        file, rank = random.choice(my_pieces)
        move_select = random.choice(
            self.board[file][rank].get_moves(self))

        turn_record = {'board': copy.deepcopy(self.board), # before the move is made
                       'piece': copy.deepcopy(self.board[file][rank]),
                       'dest': move_select} 

        p = type(self.board[file][rank]).__name__
        self.board[file][rank].make_move(move_select, self)
        
        loc = ''.join(map(str, move_select))
        print(f'{color[0].upper() + color[1:]} \
moves {p} to {loc}.')

        self.history.append(turn_record)
        return (file, rank, move_select[0], move_select[1]) # for gui. game continues.
        
    def play(self, white='human', black='cpu'):        
        while True:
            self.show()
            if white == 'human':
                game_continues = self.human_turn('white')
            else:
                game_continues = self.cpu_turn('white')
            
            self.show() 
            if game_continues:
                if black == 'cpu':
                    game_continues = self.cpu_turn('black')
                else:
                    game_continues = self.human_turn('black')
            
            if not game_continues: break

if __name__ == '__main__':
    b = Board()
    #b.play(white='human')



    #print( type(b.board['a'][2]).__name__)

    b.board['g'][1] = ' ' #Bishop('b', 'black', ('c', 3))
    b.board['f'][1] = ' ' #King('K','black',('d',6))
    b.board['f'][2] = ' '

    b.board['b'][8] = ' '
    b.board['c'][8] = ' '
    b.board['d'][8] = ' '
    b.board['d'][7] = ' '
    b.play(black='human')
    
    #b.board['d'][1] = ' '
    #b.board['d'][6] = Rook('r', 'black', ('d',6))
    #b.show()
    #b.board['e'][1].make_move(('k', 0), b)
    #b.board['f'][3] = Knight('n', 'black', ('f',3))
    #b.show()
    
    
    
    #print(b.board['e'][1].get_moves(b))

    #b.board['e'][1].make_move(('k',0), b)
    #b.show()

    


    # print(b.board['d'][2].get_moves(b))
    # print(b.board['d'][2].causes_check(('d',3), b))

    # b.show()




