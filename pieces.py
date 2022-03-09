class Piece:
    def __init__(self, kind, color, position, board, has_moved=0):
        self.kind = kind
        self.color = color
        self.file = position[0] 
        self.rank = position[1]
        self.has_moved = has_moved
        self.board = board

class Pawn(Piece):
    def get_moves(self, check=True): 
        possible_moves = []
        start_rank = 2 if self.color == 'white' else 7
        move_fwd = 1 if self.color == 'white' else -1
        if not self.has_moved and \
           self.board.is_empty((self.file, self.rank+move_fwd)) and \
           self.board.is_empty((self.file, self.rank+(move_fwd*2))):
            possible_moves.append((self.file, self.rank+(move_fwd*2)))
        if self.board.is_empty((self.file, self.rank+move_fwd)):
            possible_moves.append((self.file, self.rank+move_fwd))
        for pos in [(chr(ord(self.file)-1), self.rank+move_fwd), 
                    (chr(ord(self.file)+1), self.rank+move_fwd)]:
            if self.board.is_opponent(pos, self.color):
                possible_moves.append(pos)
        ## CHECK IF EN PASSANT POSSIBLE ##
        ep_rank = 5 if self.color == 'white' else 4
        op_pawn_rank = 7 if self.color == 'white' else 2
        if self.rank == ep_rank:
            prev_start = self.board.history[-1]['start']
            prev_end = self.board.history[-1]['end']
            prev_piece = self.board.history[-1]['piece']
            if prev_start[1] == op_pawn_rank and \
                prev_end[1] == ep_rank and prev_piece == Pawn and \
                prev_end[0] in [chr(ord(self.file)+x) for x in [1, -1]]:
                possible_moves.append((prev_start[0], 'p'))
        ## REPLACE MOVES THAT LEAD TO LAST RANK WITH PROMOTION OPTIONS
        l_rank = 8 if self.color == 'white' else 1
        last_rank = list(filter(lambda x: x[1] == l_rank, possible_moves))
        for move in last_rank:
            possible_moves.remove(move)
            promotion_options = [(move[0], str(l_rank)+x) for x in 'rnbq']
            possible_moves.extend(promotion_options)
        new = []
        og_file, og_rank = self.file, self.rank
        if check:
            for m in possible_moves:
                if not(self.board.causes_check((self.file,self.rank), m)):
                    new.append(m)
                self.file, self.rank = og_file, og_rank
                # ^manually reset to original. since new piece replaces the
                # one on which this method was called in promotions, 
                # file/rank won't be updated when the move is reversed
        return new

class Rook(Piece):
    def get_moves(self, check=True):   
        possible_moves = []
        fwd_rng = zip([self.file]*8, range(self.rank+1, 9))
        bck_rng = zip([self.file]*8, range(self.rank-1, 0, -1))
        left_rng = zip(map(chr, range(ord(self.file)-1, 96, -1)), [self.rank]*8)
        right_rng = zip(map(chr, range(ord(self.file)+1, 105)), [self.rank]*8) 
        for rng in [fwd_rng, bck_rng, left_rng, right_rng]:
            for file, rank in rng: 
                if self.board.is_empty((file, rank)):
                    possible_moves.append((file, rank))
                elif self.board.is_opponent((file, rank), self.color):
                    possible_moves.append((file, rank))
                    break
                else:
                    break 
        if check: # remove any possible moves that put the king in check
            possible_moves = [x for x in possible_moves if \
                not(self.board.causes_check((self.file,self.rank), x))]
        return possible_moves

class Knight(Piece):
    def get_moves(self, check=True):
        possible_moves = []
        # simply list all positions going clockwise from top right
        files = map(chr, [ord(self.file)+1, ord(self.file)+2, 
                          ord(self.file)+2, ord(self.file)+1, 
                          ord(self.file)-1, ord(self.file)-2,
                          ord(self.file)-2, ord(self.file)-1])
        ranks = [self.rank+2, self.rank+1, self.rank-1, self.rank-2,
                 self.rank-2, self.rank-1, self.rank+1, self.rank+2]
        for file, rank in zip(files, ranks):
            if self.board.is_empty((file, rank)) or \
               self.board.is_opponent((file, rank), self.color):
               possible_moves.append((file, rank))
        if check: # remove any possible moves that put the king in check
            possible_moves = [x for x in possible_moves if \
                not(self.board.causes_check((self.file,self.rank), x))]
        return possible_moves

class Bishop(Piece):
    def get_moves(self, check=True):
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
                if self.board.is_empty((file, rank)):
                    possible_moves.append((file, rank))
                elif self.board.is_opponent((file, rank), self.color):
                    possible_moves.append((file, rank))
                    break
                else:
                    break
        if check: # remove any possible moves that put the king in check
            possible_moves = [x for x in possible_moves if \
                not(self.board.causes_check((self.file,self.rank), x))]
        return possible_moves

class Queen(Piece):
    def get_moves(self, check=True):
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
                if self.board.is_empty((file, rank)):
                    possible_moves.append((file, rank))
                elif self.board.is_opponent((file, rank), self.color):
                    possible_moves.append((file, rank))
                    break
                else:
                    break
        if check: # remove any possible moves that put the king in check
            possible_moves = [x for x in possible_moves if \
                not(self.board.causes_check((self.file,self.rank), x))]
        return possible_moves

class King(Piece):
    def get_moves(self, check=True):
        possible_moves = []
        # starting from top right, going clockwise
        files = map(chr, [ord(self.file)+1, ord(self.file)+1, 
                          ord(self.file)+1, ord(self.file), 
                          ord(self.file)-1, ord(self.file)-1,
                          ord(self.file)-1, ord(self.file)])
        ranks = [self.rank+1, self.rank, self.rank-1, self.rank-1,
                 self.rank-1, self.rank, self.rank+1, self.rank+1]
        for file, rank in zip(files, ranks):
            if self.board.is_empty((file, rank)) or \
               self.board.is_opponent((file, rank), self.color):
               possible_moves.append((file, rank))
        # castling
        first_rank = 1 if self.color == 'white' else 8
        q_rook_still = type(self.board.at(('a', first_rank))) == Rook and \
                    self.board.at(('a', first_rank)).color == self.color and \
                    not(self.board.at(('a', first_rank)).has_moved)
        k_rook_still = type(self.board.at(('h', first_rank))) == Rook and \
                    self.board.at(('h', first_rank)).color == self.color and \
                    not(self.board.at(('h', first_rank)).has_moved)
        q_side_empty = all([self.board.is_empty((x, first_rank)) 
                        for x in 'bcd']) 
        k_side_empty = all([self.board.is_empty((x, first_rank)) 
                        for x in 'fg'])
        if not(self.has_moved) and q_rook_still and q_side_empty:
            possible_moves.append(('q', 0))
        if not(self.has_moved) and k_rook_still and k_side_empty:
            possible_moves.append(('k', 0))
        if check: # remove any possible moves that put the king in check
            possible_moves = [x for x in possible_moves if \
                not(self.board.causes_check((self.file,self.rank), x))]
        return possible_moves
