import math

PI = 3.1415926
Multiplier_AngleToRad = PI / 180


def e_dst(coord_a, coord_b):
    return math.sqrt((coord_a[0] - coord_b[0])**2 + (coord_a[1] - coord_b[1])**2)


def intersected_PointBox(coord, box):
    return True if box[0][0] <= coord[0] and coord[0] <= box[1][0] and box[0][1] <= coord[1] and coord[1] <= box[1][1] else False 


def intersected_BoxBox(box_1, box_2):
    for i in range(2):
        if box_1[0][i] > box_2[1][i] or box_2[0][i] > box_1[1][i]:
            return False
    return True
    