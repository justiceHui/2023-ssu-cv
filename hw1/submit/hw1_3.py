import sys
from checker_board import *


def solve3(filename):
    image = cv2.imread(filename)
    result = perspective_transform(image, auto_perspective_matrix(image))
    cv2.imshow(filename, result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        for file in FILE_LIST:
            solve3(FILE_PATH + file)
    else:
        solve3(sys.argv[1])
