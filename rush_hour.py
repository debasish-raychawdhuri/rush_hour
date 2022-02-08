from codecs import StreamReader
from multiprocessing.dummy import Array
import sys
import csv
print('Argument List:', str(sys.argv[0]))

row_cars = []
col_cars = []
mines = []
red_pos = ""

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
