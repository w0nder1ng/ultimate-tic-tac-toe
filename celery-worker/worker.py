from celery import Celery
from os import getenv, path, makedirs, getcwd, chmod
import subprocess
from io import BytesIO
import zipfile
import time

MAX_UPLOAD_SIZE = 10 * 1024 * 1024

app = Celery(
    "ultimate-tic-tac-toe",
    broker=getenv("CELERY_BROKER_URL", "redis://localhost:6379"),
    backend=getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379")
)

jail_options = ['-Mo', '-R', '/bin/', '-R', '/lib/', '-R', '/lib64/', '-R', '/usr/', '-R', '/sbin/', '-T', '/dev', '-R', '/dev/urandom', '--keep_caps', '--disable_proc']

def run_nsjail(filepath, args):
    return subprocess.run(["nsjail", *jail_options, "-R", filepath, "--cwd", filepath, "--", *args], capture_output=True, text=True)

bit_defs = {
    0b00: '.',
    0b01: 'X',
    0b10: 'O',
}

def board_to_string(board_x, board_o):
    return ''.join(''.join(bit_defs[((sub_x >> t) & 1) | (((sub_o >> t) & 1) << 1)] for t in range(9)) for sub_x, sub_o in zip(board_x, board_o))

def idx_to_sub(idx):
    return idx // 9, idx % 9

win_states = [
    0b111000000,
    0b000111000,
    0b000000111,
    0b100100100,
    0b010010010,
    0b001001001,
    0b100010001,
    0b001010100,
]

def win_subboard(subboard):
    for state in win_states:
        if (subboard & state) == state:
            return True
    return False

def win(board_c):
    board = 0b000000000
    for i, subboard in enumerate(board_c):
        if win_subboard(subboard):
            board |= 1 << i
    
    return win_subboard(board)

def sub_filled(board_x, board_o, sub):
    return board_x[sub[0]] & (1 << sub[1]) or board_o[sub[0]] & (1 << sub[1])

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

@app.task(name="upload_ai")
def upload_ai(user_id, file_data):
    file = BytesIO(file_data)
    try:
        with zipfile.ZipFile(file) as z:
            size = sum(zinfo.file_size for zinfo in z.filelist)
            if size > MAX_UPLOAD_SIZE:
                return redirect(request.url + "?err=File+too+large")
            folder = path.join(
                getcwd(), "uploads", user_id, time.strftime(
                    "%Y-%m-%d_%H-%M-%S")
            )
            makedirs(folder, exist_ok=True)

            for name in z.namelist():
                member = z.getinfo(name)
                extracted_path = z.extract(member, folder)
                attr = member.external_attr >> 16
                if member.is_dir():
                    chmod(extracted_path, 0o755)
                elif attr != 0:
                    attr &= 511
                    attr |= 6 << 6
                    chmod(extracted_path, attr)

            return folder
    except (zipfile.BadZipFile, ValueError) as e:
        return None

@app.task(name="play_game")
def play_game(filepath_x, filepath_o, init_time=-1, play_time=-1):
    board_x = [0b000000000] * 9
    board_o = [0b000000000] * 9
    prev_idx = -1

    x_logs = []
    o_logs = []
    
    winner = None
    
    if path.exists(path.join(filepath_x, "init")):
        res = run_nsjail(filepath_x, ["./init"])
        x_logs.append(res.stdout)
    if path.exists(path.join(filepath_o, "init")):
        res = run_nsjail(filepath_o, ["./init"])
        o_logs.append(res.stdout)

    while True:
        board = board_to_string(board_x, board_o)
        res = run_nsjail(filepath_x, ["./main", board, str(prev_idx)])
        x_logs.append(res.stdout)

        idx = int(res.stdout.split()[-1])

        if idx not in generate_valid_moves(board, prev_idx):
            winner = 'O'
            break

        sub = idx_to_sub(idx)
        board_x[sub[0]] |= 1 << sub[1]

        if win(board_x):
            winner = 'X'
            break

        board = board[:idx] + 'X' + board[idx+1:]
        prev_idx = idx

        res = run_nsjail(filepath_o, ["./main", board, str(prev_idx)])
        o_logs.append(res.stdout)

        idx = int(res.stdout.split()[-1])

        if idx not in generate_valid_moves(board, prev_idx):
            winner = 'X'
            break

        sub = idx_to_sub(idx)
        board_o[sub[0]] |= 1 << sub[1]

        if win(board_o):
            winner = 'O'
            break

        prev_idx = idx
    
    if winner == 'X':
        x_logs.append("WIN")
        o_logs.append("LOSE")
    elif winner == 'O':
        x_logs.append("LOSE")
        o_logs.append("WIN")
    else:
        x_logs.append("TIE")
        o_logs.append("TIE")
    
    return winner, x_logs, o_logs
    