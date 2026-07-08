import sys

lines = sys.stdin.read().splitlines()

board = []
reading_board = False

for line in lines:
    if line == "Board:":
        reading_board = True
        continue
    if line == "Commands:":
        break
    if reading_board:
        board.append(line)

valid_pieces = {"K", "Q", "R", "B", "N", "P"}
width = None

for line in board:
    row = line.split()

    if width is None:
        width = len(row)
    elif len(row) != width:
        print("ERROR ROW_WIDTH_MISMATCH")
        exit()

    for token in row:
        if token == ".":
            continue
        if len(token) != 2 or token[0] not in "wb" or token[1] not in valid_pieces:
            print("ERROR UNKNOWN_TOKEN")
            exit()

print_board = False

for line in lines:
    if line.strip() == "print board":
        print_board = True

if print_board:
    for row in board:
        print(row)