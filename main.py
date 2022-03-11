from board import *
import PySimpleGUI as sg
import re

def create_gui(b): # pass Board object, returns window object
    layout = []
    for rank in Board.ranks:
        row = [sg.Text(str(rank))]
        for file in Board.files:
            imgfile = square_img(b, (file, rank))
            row.append(sg.Image(source='images/'+imgfile, pad=(0,0), key=(file, rank)))
        layout.append(row)
    info  = 'Enter your move as "start end".\n'
    info += '- normal move: ex. "a2 a4"\n'
    info += '- queenside castling: "e1 q0" or "e8 q0"\n'
    info += '- kingside castling: "e1 k0" or "e8 k0"\n'
    info += '- en passant: ex. "b5 cp" (c is the end rank)\n'
    info += '- pawn promotion: ex. "a7 a8q"\n'
    info += '  - q=queen, b=bishop, n=knight, r=rook\n'
    info += '- see options: ex. "a2 moves"\n'
    info += '- undo: "undo" (reverses a full turn)'
    
    final = [[sg.Column(layout[:4], pad=(0,0)), sg.Text(info, size=(50, 9), pad=((10,3),3))]]  
    final.append(layout[4]+[sg.Text('Messages:', pad=(5,(50,3)))])
    final.append(layout[5]+[sg.Multiline('', key='-OUT.ERROR-', disabled=True, size=(33,3))])
    final.append(layout[6]+[sg.Input(key='-IN.MOVE-', size=(15, 1), do_not_clear=False)])
    final.append(layout[7]+[sg.Button('Submit', bind_return_key=True, key='-IN.SUBMIT-'),
                            sg.Button('Exit')])
    final.append([sg.Text(' ')] + list(map(lambda x: sg.Text(x, pad=(35,0)), Board.files)))
    final.append([sg.Text('View game history:'),
                  sg.Button('Previous', disabled=True, key='-IN.PREV-'),
                  sg.Button('Next', disabled=True, key='-IN.NEXT-')])
    return sg.Window('Chess', final)

def update_board(b, window, positions): # takes a fresh board and the window to update
    for file, rank in positions:
        window[(file, rank)].update(source='images/'+square_img(b, (file, rank)))

def update_view(b, window, direction):
    if direction == -1:
        b.viewstack.append(b.history.pop())
        for pos, square in zip(b.viewstack[-1]['affected'], b.viewstack[-1]['before']):
            window[pos].update(source='images/'+square)
    else:
        b.history.append(b.viewstack.pop())
        for pos, square in zip(b.history[-1]['affected'], b.history[-1]['after']):
            window[pos].update(source='images/'+square)

def input_parser(text):
    start_end = None
    if len(text) == 5: #normal, en passant, castling
        valid_entry = re.compile('[a-h][1-8] ([a-h]|q|k)([0-8]|p)')
        if valid_entry.match(text):
            start = (text[0], int(text[1]))            
            end = (text[3], 'p') if text[-1] == 'p' else \
                (text[3], int(text[4]))
            start_end = (start, end)
    elif len(text) == 6: # promotion
        valid_entry = re.compile('[a-h][1-8] [a-h][1-8][r|n|b|q]')
        if valid_entry.match(text):
            start_end = ((text[0], int(text[1])), (text[3], text[4:]))
    elif len(text) == 8: # get moves
        valid_entry = re.compile('[a-h][1-8] moves')
        if valid_entry.match(text):
            start_end = ((text[0], int(text[1])), 'moves')
    elif text == 'undo': # reverse 2 turns
        start_end = ('undo', 'undo')
    else:
        pass
    return start_end

def play_gui():
    b = Board()
    window = create_gui(b)
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == '-IN.SUBMIT-':
            move = input_parser(values['-IN.MOVE-'])
            if move:
                if move[0] == 'undo':
                    if len(b.history) > 1:
                        for i in range(2):
                            move = b.reverse_move()
                            update_board(b, window, squares_affected(
                                move['start'], move['end']))
                        window['-OUT.ERROR-'].update('')
                    else:
                        window['-OUT.ERROR-'].update('Invalid input.') 
                elif b.at(move[0]) and move[1] == 'moves':
                    options = b.at(move[0]).get_moves()
                    moves_output = move[0][0]+str(move[0][1])+': '
                    moves_output += ', '.join(map(lambda o: o[0]+str(o[1]),
                                            options))
                    window['-OUT.ERROR-'].update(moves_output) 
                else:
                    if b.at(move[0]) and move[1] in b.at(move[0]).get_moves():
                        b.make_move(move[0], move[1])
                        #update_board(move[0], move[1])
                        update_board(b, window, 
                            squares_affected(move[0], move[1]))
                        window['-OUT.ERROR-'].update('') 
                        window['-IN.PREV-'].update(disabled=False)
                    else:
                        window['-OUT.ERROR-'].update('Invalid input.')
            else:
                window['-OUT.ERROR-'].update('Invalid input.') 
        if event == '-IN.PREV-':
            # change view of board and enable 'Next' button
            update_view(b, window, -1)
            window['-IN.NEXT-'].update(disabled=False)
            # disable input box
            window['-IN.MOVE-'].update(disabled=True)
            window['-IN.SUBMIT-'].update(disabled=True)
            if b.history == []:
                window['-IN.PREV-'].update(disabled=True)
        if event == '-IN.NEXT-':
            # change view of board and enable 'Previous' button
            update_view(b, window, 1)
            window['-IN.PREV-'].update(disabled=False)
            # enable input box if view is back to current turn.
            if b.viewstack == []:
                window['-IN.MOVE-'].update(disabled=False)
                window['-IN.SUBMIT-'].update(disabled=False)
                window['-IN.NEXT-'].update(disabled=True)

play_gui()





# b = Board()
# def play_cl():
#     b.show()
#     while True:
#         move = input('enter move\n')
#         if move == 'info':
#             print(b.king)
#             print(b.at(('e',8)).file, b.at(('e',8)).rank)
#             continue
#         if 'moves' in move:
#             try:
#                 options = b.at((move[0], int(move[1]))).get_moves()
#                 for file, rank in options: print(file+str(rank))
#             except:
#                 if b.exists((move[0], int(move[1]))):
#                     print(f'{move[0]}{move[1]} is empty')
#                 else:
#                     print(f'{move[0]}{move[1]} is not a valid position')
#             continue
#         start, end = map(list, move.split(' '))
#         start[1] = int(start[1])
#         if end[1] != 'p': end[1] = int(end[1])
#         start = tuple(start)
#         end = tuple(end)
#         if len(end) == 3 and end[2] in ('rnbq'):    # promotion
#             end = (end[0], str(end[1])+end[2])

#         if b.at(start) and end in b.at(start).get_moves():
#             b.make_move(start, end)
#             b.show()
#             print(f'move was {start} to {end}\n')

#             winner = b.checkmate()
#             if winner:
#                 print(f'Checkmate. {winner} wins.\n')
#                 break

#         else:
#             print(f'{start} to {end} is not a valid move')
# play_cl()