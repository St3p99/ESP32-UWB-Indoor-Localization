import cmath

import numpy as np

from anchor import Anchor

"""
This function assume that anchor a1 is fixed in the axis origin
r1 is the distance between the tag and a1
r2 is the distance between the tag and a2
c is the distance between the two anchors
https://www.makerfabs.cc/article/esp32-uwb-indoor-positioning-test.html"""


def trilateration_2D_2A_origin(a1: Anchor, r1: float, a2: Anchor, r2: float):
    if r1 == 0:
        return a1.x, a1.y
    c = cmath.sqrt(a2.x ** 2 + a2.y ** 2)  # because a1 is equal to (0,0)
    cos_a = (r1 * r1 + c * c - r2 * r2) / (2 * r1 * c)
    x = r1 * cos_a
    y = r1 * cmath.sqrt(1 - cos_a * cos_a)

    return round(x.real, 1), round(y.real, 1)


"""
2D Trilateration with 3 anchors
it calculates the position of the tag with the intersection of the three circles with radius equals to the
distance to the tag
https://www.101computing.net/cell-phone-trilateration-algorithm/
"""


def trilateration_2D_3A(a1: Anchor, r1: float, a2: Anchor, r2: float, a3: Anchor, r3: float):
    A = 2 * a2.x - 2 * a1.x
    B = 2 * a2.y - 2 * a1.y
    C = r1 ** 2 - r2 ** 2 - a1.x ** 2 + a2.x ** 2 - a1.y ** 2 + a2.y ** 2
    D = 2 * a3.x - 2 * a2.x
    E = 2 * a3.y - 2 * a2.y
    F = r2 ** 2 - r3 ** 2 - a2.x ** 2 + a3.x ** 2 - a2.y ** 2 + a3.y ** 2

    x = (C * E - F * B) / (E * A - B * D)
    y = (C * D - A * F) / (B * D - A * E)

    return round(x.real, 1), round(y.real, 1)


"""
This function work using 2 anchor 
it calculate the position of the tag as the intersection of 2 circles centered in the anchors position
with radius equals to the distances from the tag

Using only 2 anchors, the intersections between circles are 2.
https://math.stackexchange.com/questions/256100/how-can-i-find-the-points-at-which-two-circles-intersect
"""


def trilateration_2D_2A(a1: Anchor, r1: float, a2: Anchor, r2: float):
    d = cmath.sqrt((a1.x - a2.x) ** 2 + (a1.y - a2.y) ** 2)
    l = ((r1 ** 2) - (r2 ** 2) + (d ** 2)) / (2 * d)
    h = cmath.sqrt((r1 ** 2) - (l ** 2))

    coordinates = np.zeros((2, 2))

    factor_1 = ((l / d) * (a2.x - a1.x)) + a1.x
    factor_2 = ((h / d) * (a2.y - a1.y))

    factor_3 = ((l / d) * (a2.y - a1.y)) + a1.y
    factor_4 = ((h / d) * (a2.x - a1.x))

    coordinates[0] = round((factor_1 + factor_2).real, 1), round((factor_3 - factor_4).real, 1)
    coordinates[1] = round((factor_1 - factor_2).real, 1), round((factor_3 + factor_4).real, 1)

    return coordinates


"""
Least Squares Trilateration
This function define the tag position using Multiple Anchors
its mathematical explanation is present at the follow link:
https://www.th-luebeck.de/fileadmin/media_cosa/Dateien/Veroeffentlichungen/Sammlung/TR-2-2015-least-sqaures-with-ToA.pdf
"""
def least_squares_trilateration_2D(anchors, distances):
    A, b = solve_2D(anchors, distances)

    A_T = np.transpose(A)
    product_1 = np.dot(A_T, A)
    inverse = np.linalg.inv(product_1)
    product_2 = np.dot(A_T, b)
    r = np.dot(inverse, product_2)

    return r / 2


def solve_2D(anchors, distances):
    n_anchors = len(anchors)
    n_coordinates = 2
    A = np.zeros((n_anchors - 1, n_coordinates))
    b = np.zeros(n_anchors - 1)
    i = 1
    k_l = anchors[0].x ** 2 + anchors[0].y ** 2
    while i < n_anchors:
        A[i - 1][0] = anchors[i].x - anchors[0].x
        A[i - 1][1] = anchors[i].y - anchors[0].y

        k_cur = anchors[i].x ** 2 + anchors[i].y ** 2
        b[i - 1] = distances[0] ** 2 - distances[i] ** 2 - k_l + k_cur
        i += 1
    return A, b
