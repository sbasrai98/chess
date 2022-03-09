from board import Board

b = Board()

def play():
    b.show()

    while True:
        move = input('enter move\n')
        if 'moves' in move:
            try:
                options = b.at((move[0], int(move[1]))).get_moves()
                for file, rank in options: print(file+str(rank))
            except:
                if b.exists((move[0], int(move[1]))):
                    print(f'{move[0]}{move[1]} is empty')
                else:
                    print(f'{move[0]}{move[1]} is not a valid position')
            continue
        start, end = map(list, move.split(' '))
        start[1] = int(start[1])
        if end[1] != 'p': end[1] = int(end[1])
        start = tuple(start)
        end = tuple(end)
        if len(end) == 3 and end[2] in ('rnbq'):    # promotion
            end = (end[0], str(end[1])+end[2])

        if end in b.at(start).get_moves():
            b.make_move(start, end)
            b.show()
            print(f'move was {start} to {end}\n')

            winner = b.checkmate()
            if winner:
                print(f'Checkmate. {winner} wins.\n')
                break

        else:
            print(f'{start} to {end} is not a valid move')

play()