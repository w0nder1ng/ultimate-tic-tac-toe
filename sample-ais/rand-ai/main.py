#!/usr/bin/python3

import random
import sys

def state_subboard(board, board_num):
    board = board[board_num*9:board_num*9+9]

    if board[0] == board[1] == board[2] != '.':
        return board[0]
    if board[3] == board[4] == board[5] != '.':
        return board[3]
    if board[6] == board[7] == board[8] != '.':
        return board[6]
    if board[0] == board[3] == board[6] != '.':
        return board[0]
    if board[1] == board[4] == board[7] != '.':
        return board[1]
    if board[2] == board[5] == board[8] != '.':
        return board[2]
    if board[0] == board[4] == board[8] != '.':
        return board[0]
    if board[2] == board[4] == board[6] != '.':
        return board[2]

    if '.' not in board:
        return 'T'

    return '.'

def idx_to_sub(idx):
    return idx // 9, idx % 9

def generate_valid_moves(board, prev_move):
    if prev_move == -1:
        return [i for i in range(81) if board[i] == '.']

    prev_sub = idx_to_sub(prev_move)

    states = [state_subboard(board, i) for i in range(9)]

    if states[prev_sub[1]] != '.':
        return [i for i in range(81) if board[i] == '.' and states[i // 9] == '.']

    return [i for i in range(prev_sub[1] * 9, prev_sub[1] * 9 + 9) if board[i] == '.' and states[i // 9] == '.']

def rand_ai(board, prev_move, player):
    # Choose a random move
    return generate_valid_moves(board, prev_move)[0]

board = sys.argv[1]
prev_move = int(sys.argv[2])

with open('test', 'r') as f:
    print(f.read())

print(rand_ai(board, prev_move, 'X'))
