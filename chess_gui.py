import PySimpleGUI as sg
import chess as ch

sg.theme('Dark Blue 3')  # please make your windows colorful

# layout = [[sg.Text('Your typed chars appear here:'), sg.Image(source='images/square.png', key='-OUTPUT-')],
#           [sg.Input(key='-IN-')],
#           [sg.Button('Show'), sg.Button('Exit')]]


def square_type(pos):
    if (pos[1] in [1,3,5,7] and pos[0] in ['a','c','e','g']) or \
       (pos[1] in [2,4,6,8] and pos[0] in ['b','d','f','h']):
        return 'dark'
    else:
        return 'light'

b = ch.Board()

layout = []
for rank in range(8, 0, -1):
    row = []
    for file in ['a','b','c','d','e','f','g','h']:
        square = square_type((file, rank))
        if not ch.is_empty((file, rank), b):
            color = b.board[file][rank].color
            piece = type(b.board[file][rank]).__name__
            imgfile = '_'.join([color, piece, square])+'.png'
            row.append(sg.Image(source='images/'+imgfile, pad=(0,0), key=(file, rank)))
        else:
            row.append(sg.Image(source='images/'+square+'.png', pad=(0,0), key=(file, rank)))
    layout.append(row)

layout[5].append(sg.Text('Enter your move (example: to move a pawn from a2 to a4, enter "a2 a4")'))
layout[6].append(sg.Input(key='-IN.MOVE-', do_not_clear=False))
layout[7].append(sg.Button('Submit', bind_return_key=True))

window = sg.Window('Window Title', layout)

move_counter = 0
while True:  # Event Loop
    event, values = window.read(timeout=10)
    #print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Submit':
        # change the "output" element to be the value of "input" element
        s_file, s_rank, e_file, e_rank = list(values['-IN.MOVE-'].replace(' ', ''))
        s_rank, e_rank = int(s_rank), int(e_rank)
        b.board[s_file][s_rank].make_move((e_file, e_rank), b)
        b.show()

        s_square = square_type((s_file, s_rank)) + '.png'
        window[(s_file, s_rank)].update(source='images/'+s_square)
        e_square = '_'.join([b.board[e_file][e_rank].color,
                             type(b.board[e_file][e_rank]).__name__,
                             square_type((e_file, e_rank))]) + '.png'
        window[(e_file, e_rank)].update(source='images/'+e_square)   

    # no event. just running cpu bot
    if event == sg.TIMEOUT_KEY:
        #for color in ['white', 'black']:
        if move_counter % 2 == 0: color = 'white'
        if move_counter % 2 == 1: color = 'black'
        s_file, s_rank, e_file, e_rank = b.cpu_turn(color)

        s_square = square_type((s_file, s_rank)) + '.png'
        window[(s_file, s_rank)].update(source='images/'+s_square)
        e_square = '_'.join([b.board[e_file][e_rank].color,
                                type(b.board[e_file][e_rank]).__name__,
                                square_type((e_file, e_rank))]) + '.png'
        window[(e_file, e_rank)].update(source='images/'+e_square) 
        print('move #:', move_counter)
        move_counter += 1
            
window.close()
