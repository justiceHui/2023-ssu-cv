import sys
from checker_board import *


def solve4(filename):
    # 1. load image, apply perspective transform and make blurred gray scale image
    original_image = cv2.imread(filename)
    image = perspective_transform(original_image, auto_perspective_matrix(original_image))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gray = cv2.medianBlur(gray, 9)

    # 2. circle detection using hough transform
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 2, 50, param1=55, param2=45, minRadius=15, maxRadius=30)

    # 3. get average bright of image
    n, m, avg = len(image), len(image[0]), 0
    for i in range(n):
        for j in range(m):
            avg += gray[i][j]
    avg /= n * m

    # 4. categorize circles
    white, black = [], []
    if circles is not None:
        for i in range(circles.shape[1]):
            cx, cy, radius = circles[0][i]
            cx, cy, radius = int(cx), int(cy), int(radius)
            cnt, now = 0, 0
            # 4-1. get average bright of circle
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    x, y = cx + dx, cy + dy
                    if (0 <= y < n) and (0 <= x < m):
                        cnt += 1
                        now += gray[y][x]
            # 4-2. categorize circle
            if avg * cnt < now:
                black.append((cx, cy, radius))
            else:
                white.append((cx, cy, radius))

    print('w:%d b:%d' % (len(white), len(black)))

    if DEBUG:
        result = image.copy()
        for cx, cy, radius in black:
            cv2.circle(result, (cx, cy), radius, (0, 0, 255), 2, cv2.LINE_AA)
        for cx, cy, radius in white:
            cv2.circle(result, (cx, cy), radius, (255, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow(filename + " result", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        for file in FILE_LIST:
            solve4(FILE_PATH + file)
    else:
        solve4(sys.argv[1])
