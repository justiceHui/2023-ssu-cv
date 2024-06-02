import sys
from checker_board import *


cnt = 0
src_pts = np.zeros([4, 2], dtype=np.float32)
src = None


def on_mouse(event, x, y, flags, param):
    global cnt, src_pts
    if event != cv2.EVENT_LBUTTONDOWN or cnt >= 4:
        return
    src_pts[cnt, :] = np.array([x, y]).astype(np.float32)
    cnt += 1
    if cnt == 4:
        result = perspective_transform(src, manual_perspective_matrix(src_pts))
        cv2.imshow('result', result)


def solve2(filename):
    global src, cnt
    cnt = 0
    src = cv2.imread(filename)

    cv2.namedWindow(filename)
    cv2.setMouseCallback(filename, on_mouse)

    cv2.imshow(filename, src)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        for file in FILE_LIST:
            solve2(FILE_PATH + file)
    else:
        solve2(sys.argv[1])
