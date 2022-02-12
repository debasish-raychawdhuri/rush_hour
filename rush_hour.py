from codecs import StreamReader
from multiprocessing.dummy import Array
from shutil import move
from traceback import print_tb
from z3 import *
import sys
import csv
from xmlrpc.client import Boolean
# print('Argument List:', str(sys.argv[0]))

row_cars = []
col_cars = []
mines = []
red_pos = ""
size = 0
move_limit = 0
total_cars = 1

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
    red_car_row = int(row[0])
    red_cor_col = int(row[1])
    red_pos = (red_car_row, red_cor_col)
    # The red car is the first car in it's row.
    row_cars[red_car_row].append(red_cor_col)
    for row in strreader:
        orientation = int(row[0])
        r = int(row[1])
        c = int(row[2])
        total_cars += 1
        if orientation == 1:
            row_cars[r].append(c)
        elif orientation == 0:
            col_cars[c].append(r)
        else:
            mines.append((r, c))


# print(red_pos)
# print(mines)
# print()
# print(row_cars)
# print(col_cars)

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
                row_car_vars[i][r][c].append(
                    Bool("row_car_vars[%s][%s][%s][%s]" % (i, r, c, k)))


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
                col_car_vars[i][r][c].append(
                    Bool("col_car_vars[%s][%s][%s][%s]" % (i, r, c, k)))

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
            moves[i][j][k] = (Bool("moves[%s][%s][%s]left" % (i, j, k)), Bool(
                "moves[%s][%s][%s]right" % (i, j, k)), Bool("moves[%s][%s][%s]up" % (i, j, k)), Bool("moves[%s][%s][%s]down" % (i, j, k)))

# Time to add the conditions in CNF
clauses = []

# Moves that never make sense
for i in range(move_limit):
    for j in range(size):
        clauses.append(Not(moves[i][j][size-1][1]))
        clauses.append(Not(moves[i][j][size-2][1]))
        clauses.append(Not(moves[i][j][0][0]))
    for k in range(size):
        clauses.append(Not(moves[i][size-1][k][3]))
        clauses.append(Not(moves[i][size-2][k][3]))
        clauses.append(Not(moves[i][0][k][2]))

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
# or keep the car in the same place if no move
for i in range(move_limit):
    for j in range(size):
        for k in range(size):
            m = moves[i][j][k]
            row_car_vars_for_row = row_car_vars[i][j]

            for ci in range(len(row_car_vars_for_row)):
                car = row_car_vars_for_row[ci]
                car_k = car[k]
                no_moves = []
                if k != 0:
                    clauses.append(
                        Or(Not(car_k), Not(moves[i][j][k][0]), row_car_vars[i+1][j][ci][k-1]))

                if k < size-1:
                    clauses.append(
                        Or(Not(car_k), Not(moves[i][j][k][1]), row_car_vars[i+1][j][ci][k+1]))

                no_moves.append(moves[i][j][k][0])
                no_moves.append(moves[i][j][k][1])
                clauses.append(
                    Or(Not(car_k), *no_moves, row_car_vars[i+1][j][ci][k]))

            col_car_vars_for_col = col_car_vars[i][k]
            for ci in range(len(col_car_vars_for_col)):
                car = col_car_vars_for_col[ci]
                car_j = car[j]
                no_moves = []
                if j != 0:
                    clauses.append(
                        Or(Not(car_j), Not(moves[i][j][k][2]), col_car_vars[i+1][k][ci][j-1]))

                if j < size-1:
                    clauses.append(
                        Or(Not(car_j), Not(moves[i][j][k][3]), col_car_vars[i+1][k][ci][j+1]))

                no_moves.append(moves[i][j][k][2])
                no_moves.append(moves[i][j][k][3])
                clauses.append(
                    Or(Not(car_j), *no_moves, col_car_vars[i+1][k][ci][j]))

# A car can only be at one place at a time
for i in range(move_limit+1):
    for j in range(size):
        for car in row_car_vars[i][j]:
            bool = Bool("red[%s][%s][%s]" % (i, j, car))
            clauses.append(Not(car[size-1]))
            for k in range(size):
                new_bool = Bool("red_row[%s][%s][%s][%s]" % (i, j, car, k))
                clauses.append(Or(Not(bool), new_bool))
                clauses.append(Or(Not(car[k]), new_bool))
                clauses.append(Or(Not(bool), Not(car[k])))
                bool = new_bool

for i in range(move_limit+1):
    for k in range(size):
        for car in col_car_vars[i][k]:
            bool = Bool("red_[%s][%s][%s]" % (i, j, car))
            clauses.append(Not(car[size-1]))
            for j in range(size):
                new_bool = Bool("red_col[%s][%s][%s][%s]" % (i, k, car, j))
                clauses.append(Or(Not(bool), new_bool))
                clauses.append(Or(Not(car[j]), new_bool))
                clauses.append(Or(Not(bool), Not(car[j])))
                bool = new_bool

# cars don't step on a mine
for i in range(move_limit+1):
    for mine in mines:
        (j, k) = mine
        for car in row_car_vars[i][j]:
            clauses.append(Not(car[k]))
        for car in col_car_vars[i][k]:
            clauses.append(Not(car[j]))

# Only one move per move


for i in range(move_limit):
    v = Bool("movesss")
    for j in range(size):
        for k in range(size):
            for l in range(4):
                nv = Bool("movesss[%s][%s][%s][%s]" % (i, j, k, l))
                clauses.append(Or(Not(v), Not(moves[i][j][k][l])))
                clauses.append(Or(Not(v), nv))
                clauses.append(Or(Not(moves[i][j][k][l]), nv))
                v = nv

# cars don't collide, a.k.a. for every time slot, for every
# square, there should be only one car in it.


# time -> row -> column -> (1+row_cars + col_cars)
# first remember the position of only the current row and column
square_threads_row = []
square_threads_col = []
for i in range(move_limit+1):
    square_threads_row.append(None)
    square_threads_row[i] = []
    square_threads_col.append(None)
    square_threads_col[i] = []
    for j in range(size):
        square_threads_row[i].append(None)
        square_threads_row[i][j] = []
        square_threads_col[i].append(None)
        square_threads_col[i][j] = []
        for k in range(size):
            square_threads_row[i][j].append(None)
            square_threads_row[i][j][k] = Bool(
                "square_threads_row[%s][%s][%s]" % (i, j, k))
            square_threads_col[i][j].append(None)
            square_threads_col[i][j][k] = Bool(
                "square_threads_col[%s][%s][%s]" % (i, j, k))
            for car in row_car_vars[i][j]:
                car_k = car[k]
                old_thread = square_threads_row[i][j][k]
                new_thread = Bool(
                    "square_threads_row[%s][%s][%s][%s]" % (i, j, k, car))
                clauses.append(Or(Not(old_thread), new_thread))
                clauses.append(Or(Not(car_k), new_thread))
                clauses.append(Or(Not(old_thread), Not(car_k)))
                square_threads_row[i][j][k] = new_thread
            for car in col_car_vars[i][k]:
                car_j = car[j]
                old_thread = square_threads_col[i][j][k]
                new_thread = Bool(
                    "square_threads_col[%s][%s][%s][%s]" % (i, j, k, car))
                clauses.append(Or(Not(old_thread), new_thread))
                clauses.append(Or(Not(car_j), new_thread))
                clauses.append(Or(Not(old_thread), Not(car_j)))
                square_threads_col[i][j][k] = new_thread

# Now we disallow collision between different rows and columns
for i in range(move_limit+1):
    for j in range(size):
        clauses.append(Not(square_threads_row[i][j][size-1]))
        clauses.append(Not(square_threads_row[i][j][size-2]))
for i in range(move_limit+1):
    for k in range(size):
        clauses.append(Not(square_threads_col[i][size-1][k]))
        clauses.append(Not(square_threads_col[i][size-2][k]))
for i in range(move_limit+1):
    for j in range(size):
        for k in range(size):
            clauses.append(
                Or(Not(square_threads_row[i][j][k]), Not(square_threads_col[i][j][k])))
            if j > 0:
                clauses.append(
                    Or(Not(square_threads_row[i][j][k]), Not(square_threads_col[i][j-1][k])))
                clauses.append(
                    Or(Not(square_threads_col[i][j-1][k]), Not(square_threads_col[i][j][k])))
            if k > 0:
                clauses.append(
                    Or(Not(square_threads_row[i][j][k-1]), Not(square_threads_col[i][j][k])))
                clauses.append(
                    Or(Not(square_threads_row[i][j][k]), Not(square_threads_row[i][j][k-1])))
            if j > 0 and k > 0:
                clauses.append(
                    Or(Not(square_threads_row[i][j][k-1]), Not(square_threads_col[i][j-1][k])))

            # Initial and final conditions
for j in range(size):
    row = row_cars[j]
    for c in range(len(row)):
        k = row[c]
        for l in range(size):
            if l != k:
                clauses.append(Not(row_car_vars[0][j][c][l]))
        clauses.append(row_car_vars[0][j][c][k])
for k in range(size):
    col = col_cars[k]
    for c in range(len(col)):
        j = col[c]
        for l in range(size):
            if l != j:
                clauses.append(Not(col_car_vars[0][k][c][l]))
        clauses.append(col_car_vars[0][k][c][j])
clauses.append(row_car_vars[move_limit][red_pos[0]][0][size-2])

solver = Solver()
solver.add(And(*clauses))
if solver.check() == sat:
    model = solver.model()
    for i in range(move_limit):
        # print("=================================================")
        # for j in range(size):
        #     print("Row cars")
        #     for car in row_car_vars[i][j]:
        #         for k in car:
        #             if model[k] == True:
        #                 print(k)
        # for k in range(size):
        #     print("Col cars")
        #     for car in col_car_vars[i][k]:
        #         for j in car:
        #             if model[j] == True:
        #                 print(j)
        # for j in range(size):
        #     for k in range(size):
        #         for l in range(4):
        #             if model[moves[i][j][k][l]] == True:
        #                 print(moves[i][j][k][l])
        for j in range(size):
            for k in range(size):
                if model[moves[i][j][k][0]] == True or model[moves[i][j][k][2]] == True:
                    print("%s,%s" % (j, k))
                elif model[moves[i][j][k][1]] == True:
                    print("%s,%s" % (j, k+1))
                elif model[moves[i][j][k][3]] == True:
                    print("%s,%s" % (j+1, k))

else:
    print("unsat")
