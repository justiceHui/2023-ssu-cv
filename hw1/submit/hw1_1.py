import sys
from checker_board import *


# check that given segment is proper edge by random sampling
def get_diff_random_sample(gray_image, p1: Point2D, p2: Point2D, sampling=15):
    n, m = len(gray_image), len(gray_image[0])
    if p1.x > p2.x or (p1.x == p2.x and p1.y > p2.y):
        (p1, p2) = (p2, p1)

    res = []
    for _ in range(sampling):
        p_rnd = Line2D(p1, p2).random_point()
        ang = random.uniform(0, math.pi)
        s, c = math.sin(ang), math.cos(ang)
        chk1 = Point2D(math.floor(p_rnd.x + c * 3), math.floor(p_rnd.y + s * 3))
        chk2 = Point2D(math.floor(p_rnd.x - c * 3), math.floor(p_rnd.y - s * 3))
        if (0 <= chk1.x < n) and (0 <= chk1.y < m) and (0 <= chk2.x < n) and (0 <= chk2.y < m):
            res.append(abs(int(gray_image[chk1.x][chk1.y]) - int(gray_image[chk2.x][chk2.y])))

    res.sort()
    if len(res) == 0:
        return 0
    return res[len(res) // 2]


# check two lines are parallel or orthogonal
def is_orthogonal(l1: Line2D, l2: Line2D, base=math.pi/2) -> bool:
    ang = l1.get_angle(l2)
    return abs(ang) < 0.1 or abs(ang - base) < 0.2


# check that lines are orthogonal to each other
def check_lines_orthogonal_threshold(lines_with_diff: list[(float, Line2D)], threshold: float) -> bool:
    for i in range(len(lines_with_diff)):
        if lines_with_diff[i][0] <= threshold:
            break
        for j in range(i + 1, len(lines_with_diff)):
            if lines_with_diff[j][0] <= threshold:
                break
            if not is_orthogonal(lines_with_diff[i][1], lines_with_diff[j][1]):
                return False
    return True


# grouping segments which are close to each other and have similar angles
def bfs_group(lines: list[Line2D], angle_threshold) -> list[Line2D]:
    res, chk = [], [0 for _ in range(len(lines))]

    def bfs_group_run(st) -> Line2D:
        group, que, fr = [], [], 0
        que.append(st)
        chk[st] = 1
        while fr < len(que):
            v = que[fr]
            fr += 1
            group.append(lines[v])
            for i in range(len(lines)):
                if chk[i] == 1 or lines[v].get_angle(lines[i]) > angle_threshold:
                    continue
                if segment_distance(lines[v], lines[i]) < 5:
                    que.append(i)
                    chk[i] = 1

        group.sort(key=lambda x: math.atan2(lines[i].vec.y, lines[i].vec.x))
        return group[len(group) // 2]

    for s in range(len(lines)):
        if chk[s] == 0:
            res.append(bfs_group_run(s))
    return res


# get slope of axis(pair of most orthogonal lines)
def get_most_orthogonal_axis(lines: list[Line2D]):
    if len(lines) <= 2:
        return lines
    mx, l1, l2 = 0, 0, 1
    for i in range(len(lines)):
        for j in range(i+1, len(lines)):
            if not segment_intersect(lines[i], lines[j]):
                continue
            ang = lines[i].get_angle(lines[j])
            if ang > mx:
                mx, l1, l2 = ang, i, j
    return lines[l1], lines[l2]


# get segments connected and orthogonal to axis lines
def bfs_line(lines: list[Line2D], axis: (Line2D, Line2D)) -> list[Line2D]:
    st = 0
    for line in lines:
        if (line.a, line.b, line.c) == (axis[0].a, axis[0].b, axis[0].c):
            break
        else:
            st += 1
    axis_angle = axis[0].get_angle(axis[1])

    res, chk, que, fr = [], [0 for _ in range(len(lines))], [], 0
    que.append(st)
    while fr < len(que):
        v = que[fr]
        fr += 1
        res.append(lines[v])
        for i in range(len(lines)):
            if chk[i] == 1 or segment_distance(lines[v], lines[i]) > 5:
                continue
            if abs(lines[v].get_angle(lines[i]) - axis_angle) > 0.1:
                continue
            que.append(i)
            chk[i] = 1
    return res


# get edges of image
def extract_edges(image):
    # 1. make blurred gray scale image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 0)
    sz = (len(image), len(image[0]))

    # 2. edge detection using hough transform
    edge = cv2.Canny(image, 50, 200, 3)
    hough = cv2.HoughLinesP(edge, 1, math.pi / 180, 120, minLineLength=min(sz[0], sz[1]) // 10, maxLineGap=10)

    # 3. remove non-proper edges

    # 3-1. get line's score
    lines = []
    lines_with_diff = []
    for i in range(hough.shape[0]):
        pt1 = Point2D(hough[i][0][1], hough[i][0][0])
        pt2 = Point2D(hough[i][0][3], hough[i][0][2])
        lines_with_diff.append((get_diff_random_sample(gray, pt1, pt2), Line2D(pt1, pt2)))

    # 3-2. get line score threshold using binary search
    le, ri = 0, 256
    while le < ri:
        md = (le + ri) // 2
        if check_lines_orthogonal_threshold(lines_with_diff, md):
            ri = md
        else:
            le = md + 1
    line_threshold = (ri * 3 + 3) // 4

    # 3-3. remove non-proper line
    for diff, l in lines_with_diff:  # remove low-scored lines
        if diff >= line_threshold:
            lines.append(l)

    lines = bfs_group(lines, 0.1)  # grouping similar lines
    axis = get_most_orthogonal_axis(lines)
    lines = bfs_line(lines, axis)  # remove lines not connected to axis

    return lines, axis


def solve1(filename):
    # 1. load image, apply perspective transform and make blurred gray scale image
    original_image = cv2.imread(filename)
    image = perspective_transform(original_image, auto_perspective_matrix(original_image))

    # 2. get edges
    lines, axis = extract_edges(image)

    # 3. get internal corners (intersection points of lines) and calculate grid width
    intersect_points = []
    for i in range(len(lines)):
        for j in range(i+1, len(lines)):
            flag, pt = lines[i].intersect(lines[j])
            if flag and on_board(image, pt):
                intersect_points.append(pt)

    min_dst, p1, p2 = 1e9, 0, 0
    for i in range(len(intersect_points)):
        for j in range(i+1, len(intersect_points)):
            dst = intersect_points[i].dist(intersect_points[j])
            if 38 <= dst < min_dst:
                min_dst = dst
                p1, p2 = i, j

    # 4. get number of rows and columns
    row, col = 0, 0
    for i in range(-15, 15):
        pt = intersect_points[p1].add(Point2D(i * min_dst, 0))
        if on_board(image, pt):
            row += 1

    for i in range(-15, 15):
        pt = intersect_points[p1].add(Point2D(0, i * min_dst))
        if on_board(image, pt):
            col += 1

    # 6. finally, calculate answer
    res = 8 if max(row, col) <= 10 else 10
    print(res, '*', res)

    if DEBUG:
        result = image.copy()
        for line in lines:
            draw_line(result, line, (255, 0, 0), 4)
        for line in axis:
            draw_line(result, line, (255, 255, 0), 2)
        for p in intersect_points:
            draw_point(result, p, (0, 255, 255))
        draw_point(result, intersect_points[p1], (0, 0, 255))
        draw_point(result, intersect_points[p2], (0, 0, 255))

        cv2.imshow(filename, result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        for file in FILE_LIST:
            solve1(FILE_PATH + file)
    else:
        solve1(sys.argv[1])
