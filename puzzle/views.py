
from distutils.sysconfig import get_makefile_filename
from re import split
from wsgiref.handlers import format_date_time
from django.shortcuts import render
from numpy import array

from puzzle.algo import bestsolution, evaluvate, evaluvate_misplaced

path_moves = None
total_moves = 0


def solve(initial_pieces, final_pieces):
    global total_moves
    global path_moves
    state, visited = evaluvate(initial_pieces, final_pieces)
    best_path = bestsolution(state)
    total_moves = len(best_path) - 1
    path_moves = [None] * (total_moves + 1)
    for step in range(total_moves+1):
        pieces = split('', str(best_path[step]).replace(
            '[', '').replace(']', '').replace('\n', '').replace(' ', ''))
        pieces = list(filter(lambda a: a != '', pieces))
        path_moves[step] = pieces

    print(path_moves)
    print('Steps to reach goal:', total_moves)
    visit = len(state) - visited
    print('Total nodes visited: ', visit, "\n")


processing = False


def index(request):
    global processing
    global path_moves
    initial_state_pieces = []
    final_state_pieces = []
    path_moves = None
    if request.method == 'POST':
        # Extract the initial state numbers from the hidden fields
        for i in range(9):
            val = request.POST.get('initStatePiece_{}'.format(i))
            initial_state_pieces.append(0 if val == '' else int(val))

        # Extract the goal state numbers from the text fields
        for i in range(9):
            val = request.POST.get('finalStatePiece_{}'.format(i))
            final_state_pieces.append(0 if val == '' else int(val))

        if(not processing):
            processing = True
            solve(initial_state_pieces, final_state_pieces)

    return render(request, 'index.html', {'range': range(0, 9), 'path_moves': path_moves, 'total_moves': total_moves})
