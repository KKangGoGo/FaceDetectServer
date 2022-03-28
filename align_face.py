import math
import numpy as np


def euclidean_distance(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return math.sqrt(((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)))


def align_angle(left_eye, right_eye):
    # 회전 방향 결정
    if left_eye[1] <= right_eye[1]:  # 오른쪽 눈이 높으면 시계방향
        direction = -1
        point_3rd = (right_eye[0], left_eye[1])
    else:  # 반시계방향
        direction = 1
        point_3rd = (left_eye[0], right_eye[1])

    a = euclidean_distance(left_eye, point_3rd)
    b = euclidean_distance(right_eye, left_eye)
    c = euclidean_distance(right_eye, point_3rd)

    cos_a = (b * b + c * c - a * a) / (2 * b * c)
    print("cos(a) = ", cos_a)

    angle = np.arccos(cos_a)
    print("angle: ", angle, " in radian")

    angle = (angle * 180) / math.pi
    print("angle: ", angle, " in degree")

    if direction == -1:
        angle = 90 - angle
    return angle * direction
