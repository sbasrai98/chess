import PySimpleGUI as sg
import chess as ch
import re
import pickle
import datetime

sg.theme('Dark Blue 3')  

def square_type(pos):
    if (pos[1] in [1,3,5,7] and pos[0] in ['a','c','e','g']) or \
       (pos[1] in [2,4,6,8] and pos[0] in ['b','d','f','h']):
        return 'dark'
    else:
        return 'light'

def reset_board(b, window): # takes a fresh board and the window to update
    for rank in ch.Board.ranks:
        for file in ch.Board.files:
            square = square_type((file, rank))
            if not ch.is_empty((file, rank), b):
                color = b.board[file][rank].color
                piece = type(b.board[file][rank]).__name__
                imgfile = '_'.join([color, piece, square])+'.png'
                window[(file, rank)].update(source='images/'+imgfile)
            else:
                window[(file, rank)].update(source='images/'+square+'.png')

b = ch.Board()
layout = []
for rank in ch.Board.ranks:
    row = [sg.Text(str(rank))]
    for file in ch.Board.files:
        square = square_type((file, rank))
        if not ch.is_empty((file, rank), b):
            color = b.board[file][rank].color
            piece = type(b.board[file][rank]).__name__
            imgfile = '_'.join([color, piece, square])+'.png'
            row.append(sg.Image(source='images/'+imgfile, pad=(0,0), key=(file, rank)))
        else:
            row.append(sg.Image(source='images/'+square+'.png', pad=(0,0), key=(file, rank)))
    layout.append(row)

layout[4].append(sg.Text('Enter your move (example: to move a pawn from a2 to a4, enter "a2 a4")'))
layout[5].append(sg.Text('', key='-OUT.ERROR-'))
layout[6].append(sg.Input(key='-IN.MOVE-', do_not_clear=False))
layout[7].append(sg.Button('Submit', bind_return_key=True))
layout.append(list(map(lambda x: sg.Text(x, pad=(36,0)), ch.Board.files)))
window = sg.Window('Chess', layout)

valid_entry = re.compile('[a-h][1-8] ([a-h]|q|k)[0-8]')
while True:  # Event Loop
    event, values = window.read(timeout=5) # timeout=5
    #print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'Submit':
        # change the "output" element to be the value of "input" element
        if valid_entry.match(values['-IN.MOVE-']):
            s_file, s_rank, e_file, e_rank = list(values['-IN.MOVE-'].replace(' ', ''))
            s_rank, e_rank = int(s_rank), int(e_rank)
            if (e_file, e_rank) in b.board[s_file][s_rank].get_moves(b):
                b.board[s_file][s_rank].make_move((e_file, e_rank), b)
                b.show()
                s_square = square_type((s_file, s_rank)) + '.png'
                window[(s_file, s_rank)].update(source='images/'+s_square)
                e_square = '_'.join([b.board[e_file][e_rank].color,
                                    type(b.board[e_file][e_rank]).__name__,
                                    square_type((e_file, e_rank))]) + '.png'
                window[(e_file, e_rank)].update(source='images/'+e_square)  
                window['-OUT.ERROR-'].update('')     
            else:
                window['-OUT.ERROR-'].update('Not a valid move for that piece.')
        else:
            window['-OUT.ERROR-'].update('Incorrect format.')

    # no event. just running cpu bot
    if event == sg.TIMEOUT_KEY:
        if len(b.history) % 2 == 0: color, opp = 'white', 'Black'
        if len(b.history) % 2 == 1: color, opp = 'black', 'White'
        # check if only kings left
        all_squares = []
        for file in ch.Board.files:
            for rank in ch.Board.ranks:
                all_squares.append(b.board[file][rank])
        if all_squares.count(' ') == 62:
            window['-OUT.ERROR-'].update('Draw.')
            b = ch.Board()
            reset_board(b, window)

        else:
            try:
                s_file, s_rank, e_file, e_rank = b.cpu_turn(color)
                s_square = square_type((s_file, s_rank)) + '.png'
                window[(s_file, s_rank)].update(source='images/'+s_square)
                e_square = '_'.join([b.board[e_file][e_rank].color,
                                        type(b.board[e_file][e_rank]).__name__,
                                        square_type((e_file, e_rank))]) + '.png'
                window[(e_file, e_rank)].update(source='images/'+e_square) 
                print('move #:', len(b.history))
            except: # cpu_turn returned False, game is over
                window['-OUT.ERROR-'].update(opp+' wins.')
                # save the game
                fname = str(datetime.datetime.now())
                with open('saved_games/'+fname, 'wb') as fout:
                   pickle.dump(b.history, fout)
                b = ch.Board()
                reset_board(b, window)
                            
window.close()
