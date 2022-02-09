from codecs import StreamReader
from multiprocessing.dummy import Array
from shutil import move
from z3 import *
import sys
import csv
from xmlrpc.client import Boolean
print('Argument List:', str(sys.argv[0]))

row_cars = []
col_cars = []
mines = []
red_pos = ""
size = 0
move_limit = 0

with open(sys.argv[1], newline='') as csvfile:
    strreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    row = next(strreader)
    size = int(row[0])
    move_limit = int(row[1])
    row_cars = [[]] * size
    col_cars = [[]] * size

    for r in range(size):
        row_cars[r] = []
        col_cars[r] = []

    row = next(strreader)
    red_car_x = int(row[0])
    red_cor_y = int(row[1])
    red_pos = (red_car_x, red_cor_y)
    for row in strreader:
        orientation = int(row[0])
        r = int(row[1])
        c = int(row[2])
        if orientation == 1:
            row_cars[r].append(c)
        elif orientation == 0:
            col_cars[c].append(r)
        else:
            mines.append((r, c))

print(red_pos)
print(mines)
print()
print(row_cars)
print(col_cars)

# time -> row -> car -> array of bools
row_car_vars = []
for i in range(move_limit+1):
    row_car_vars.append(None)
    row_car_vars[i] = []
    for r in range(len(row_cars)):
        row = row_cars[r]
        row_car_vars[i].append([])
        for c in range(len(row)):
            car = row[c]
            # cars are arranged by rows for use later
            row_car_vars[i][r].append([])
            for k in range(size):
                row_car_vars[i][r][c].append(Bool("y"))


# time -> col -> car -> array of bools
col_car_vars = [move_limit+1]
for i in range(move_limit+1):
    col_car_vars.append(None)
    col_car_vars[i] = []
    for r in range(len(col_cars)):
        col = col_cars[r]
        col_car_vars[i].append([])
        for c in range(len(col)):
            car = col[c]
            # cars are arranged by rows for use later
            col_car_vars[i][r].append([])
            for k in range(size):
                col_car_vars[i][r][c].append(Bool("y"))

# time -> row -> col -> direction
moves = []
for i in range(move_limit):
    moves.append(None)
    moves[i] = []
    for j in range(size):
        moves[i].append(None)
        moves[i][j] = []
        for k in range(size):
            moves[i][j].append(None)
            moves[i][j][k] = (Bool("left"), Bool(
                "right"), Bool("up"), Bool("down"))

# Time to add the conditions in CNF
clauses = []

# A move is only allowed if a proper kind of car is at the correct cell
for i in range(move_limit):
    for j in range(size):
        for k in range(size):
            row_car_vars_for_row = row_car_vars[i][j]
            # make a list of row cars for particular row and column
            vs = []
            for car in row_car_vars_for_row:
                vs.append(car[k])

            clauses.append(Or(Not(moves[i][j][k][0]), *vs))
            clauses.append(Or(Not(moves[i][j][k][1]), *vs))

            col_car_vars_for_col = col_car_vars[i][k]
            vs = []
            for car in col_car_vars_for_col:
                vs.append(car[j])

            clauses.append(Or(Not(moves[i][j][k][2]), *vs))
            clauses.append(Or(Not(moves[i][j][k][3]), *vs))

# effect of a move - move the car
for i in range(move_limit):
    for j in range(size):
        for k in range(size):
            m = moves[i][j][k]
            row_car_vars_for_row = row_car_vars[i][j]

            for ci in range(len(row_car_vars_for_row)):
                car = row_car_vars_for_row[ci]
                car_k = car[k]

                if k != 0:
                    clauses.append(
                        Or(Not(car_k), Not(moves[i][j][k][0]), row_car_vars[i+1][j][ci][k-1]))
                if k < size-1:
                    clauses.append(
                        Or(Not(car_k), Not(moves[i][j][k][1]), row_car_vars[i+1][j][ci][k+1]))

            col_car_vars_for_col = col_car_vars[i][k]
            for ci in range(len(col_car_vars_for_col)):
                car = col_car_vars_for_col[ci]
                car_j = car[j]

                if j != 0:
                    clauses.append(
                        Or(Not(car_j), Not(moves[i][j][k][2]), col_car_vars[i+1][k][ci][j-1]))
                if j < size-1:
                    clauses.append(
                        Or(Not(car_j), Not(moves[i][j][k][3]), col_car_vars[i+1][k][ci][j+1]))

# cars don't step on a mine
for i in range(move_limit):
    for mine in mines:
        (j, k) = mine
        row_car_vars[i][j][k]
