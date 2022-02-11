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
    red_car_row = int(row[0])
    red_cor_col = int(row[1])
    red_pos = (red_car_row, red_cor_col)
    row_cars[red_car_row].append(red_cor_col)
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
                    no_moves.append(moves[i][j][k][0])
                if k < size-1:
                    clauses.append(
                        Or(Not(car_k), Not(moves[i][j][k][1]), row_car_vars[i+1][j][ci][k+1]))
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
                    no_moves.append(moves[i][j][k][2])
                if j < size-1:
                    clauses.append(
                        Or(Not(car_j), Not(moves[i][j][k][3]), col_car_vars[i+1][k][ci][j+1]))
                    no_moves.append(moves[i][j][k][3])
                clauses.append(
                    Or(Not(car_j), *no_moves, col_car_vars[i+1][k][ci][j]))

# cars don't step on a mine
for i in range(move_limit):
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
square_threads = []
for i in range(move_limit+1):
    square_threads.append(None)
    square_threads[i] = []
    for j in range(size):
        square_threads[i].append(None)
        square_threads[i][j] = []
        for k in range(size):
            square_threads[i][j].append(None)
            square_threads[i][j][k] = [
                Bool("square_threads[%s][%s][%s]" % (i, j, k))]
            old_thread = square_threads[i][j][k][0]
            for car in row_car_vars[i][j]:
                car_var = car[k]
                clauses.append(Or(Not(old_thread), Not(car_var)))
                new_thread = Bool(
                    "square_threads[%s][%s][%s][%s]" % (i, j, k, car_var))
                clauses.append(Or(Not(old_thread), new_thread))
                clauses.append(Or(Not(car_var), new_thread))
                if k > 0:
                    car_var_left = car[k-1]
                    clauses.append(Or(Not(old_thread), Not(car_var_left)))
                    clauses.append(Or(Not(car_var_left), Not(car_var)))
                old_thread = new_thread
            for car in col_car_vars[i][k]:
                car_var = car[j]
                clauses.append(Or(Not(old_thread), Not(car_var)))
                new_thread = Bool("square_threads[%s][%s][%s][%s]" % (
                    i, j, k, car_var))
                clauses.append(Or(Not(old_thread), new_thread))
                clauses.append(Or(Not(car_var), new_thread))
                if j > 0:
                    car_var_up = car[j-1]
                    clauses.append(Or(Not(old_thread), Not(car_var_up)))
                    clauses.append(Or(Not(car_var_up), Not(car_var)))
                old_thread = new_thread


# Initial and final conditions
for j in range(size):
    row = row_cars[j]
    for c in range(len(row)):
        k = row[c]
        clauses.append(row_car_vars[0][j][c][k])
for k in range(size):
    col = col_cars[k]
    for c in range(len(col)):
        j = col[c]
        clauses.append(col_car_vars[0][k][c][j])
row_car_vars[move_limit][red_pos[0]][0][size-2]

solver = Solver()
solver.add(And(*clauses))
if solver.check() == sat:
    model = solver.model()
    for i in range(move_limit):
        for j in range(size):
            for k in range(size):
                for l in range(4):
                    if model[moves[i][j][k][l]] == True:
                        print(moves[i][j][k][l])
else:
    print("unsat")
