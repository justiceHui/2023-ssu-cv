import cv2
import numpy as np

from my_geometry import *

DEBUG = False

FILE_PATH = './images/'
FILE_LIST = ('img1.png', 'img2.jpg', 'img3.jpg', 'img4.jpg', 'img5.jpg', 'img6.jpg', 'img7.jpg', 'img8.jpg')
SIZE = 500


def draw_line(image, line: Line2D, color=(255, 0, 0), thinkness=3):
    if line.b == 0:
        cv2.line(image, (0, int(-line.c)), (len(image[0]) - 1, int(-line.c)), color, thickness=thinkness)
    else:
        x1, x2 = 0, len(image) - 1
        y1, y2 = line.calc(x1), line.calc(x2)
        cv2.line(image, (int(y1), x1), (int(y2), x2), color, thickness=thinkness)


def draw_point(image, pt: Point2D, color=(0, 0, 255), sz=3):
    n, m = len(image), len(image[0])
    for dx in range(-sz, sz+1):
        for dy in range(-sz, sz+1):
            x, y = int(pt.x + dx), int(pt.y + dy)
            if (0 <= x < n) and (0 <= y < m):
                image[x][y] = color


def on_board(image, pt: Point2D) -> bool:
    return (0 <= pt.x < len(image)) and (0 <= pt.y < len(image[0]))


# get proper convex quadrilaterals contains every points
def make_to_quadrilaterals(points: list[Point2D]) -> list[Point2D]:
    v = convex_hull(points)
    lines = []
    for i in range(len(v)):
        p1, p2 = v[i], v[(i + 1) % len(v)]
        lines.append((p1.dist(p2), Line2D(p1, p2), i))
    lines.sort(key=lambda x: -x[0])
    lines = lines[:4]
    lines.sort(key=lambda x: x[2])
    res = []
    for i in range(4):
        res.append(lines[i][1].intersect(lines[(i + 1) % 4][1])[1])
    return res


def manual_perspective_matrix(src_pts: np.ndarray):
    assert src_pts.shape == (4, 2)
    dst_pts = np.float32([[0, 0], [SIZE, 0], [SIZE, SIZE], [0, SIZE]])
    return cv2.getPerspectiveTransform(src_pts, dst_pts)


def auto_perspective_matrix(image):
    # 1. make gray scale image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 0)
    sz = (len(image), len(image[0]))

    # 2. edge detection using hough transform
    edge = cv2.Canny(image, 50, 200, 3)
    hough = cv2.HoughLinesP(edge, 1, math.pi/180, 120, minLineLength=min(sz[0], sz[1])//40, maxLineGap=20)

    hough_image = gray.copy()
    hough_image[hough_image < 256] = 0

    for i in range(hough.shape[0]):
        pt1 = (hough[i][0][0], hough[i][0][1])
        pt2 = (hough[i][0][2], hough[i][0][3])
        cv2.line(hough_image, pt1, pt2, (255, 255, 255), thickness=1)

    # 3. find external contours
    contours, _ = cv2.findContours(hough_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 4. get convex hull using Graham's scan to make quadrilaterals
    points = np.vstack(contours).squeeze()
    hull = []
    for p in points:
        hull.append(Point2D(p[1], p[0]))
    hull = make_to_quadrilaterals(hull)[::-1]

    # 5. get perspective transform matrix
    points_list = [[int(p.y), int(p.x)] for p in hull]
    return manual_perspective_matrix(np.float32(points_list))


def perspective_transform(image, transform_matrix):
    return cv2.warpPerspective(image, transform_matrix, (SIZE, SIZE))
