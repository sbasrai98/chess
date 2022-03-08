from board import Board

b = Board()

def play():
    b.show()

    while True:
        move = input('enter move\n')
        start, end = map(list, move.split(' '))
        start[1] = int(start[1])
        if end[1] != 'p': end[1] = int(end[1])
        start = tuple(start)
        end = tuple(end)

        #print(b.at(start).get_moves())

        if end in b.at(start).get_moves():
            b.move_piece(start, end)
            b.show()
            print(f'move was {start} to {end}\n')
        else:
            print(f'{start} to {end} is not a valid move\n')

play()