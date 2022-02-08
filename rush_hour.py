from codecs import StreamReader
from multiprocessing.dummy import Array
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
row_car_vars = [move_limit]
for i in range(move_limit+1):
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

col_car_vars = [move_limit+1]

for i in range(move_limit+1):
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
