import math
import random
import copy


# Basic class for 2D coordinate point
class Point2D:
    def __init__(self, _x, _y):
        self.x = _x
        self.y = _y

    def add(self, other): return Point2D(self.x + other.x, self.y + other.y)

    def sub(self, other): return Point2D(self.x - other.x, self.y - other.y)

    def to_int(self): return Point2D(int(self.x), int(self.y))

    def less_than(self, other): return self.x < other.x or (self.x == other.x and self.y < other.y)

    def len(self): return math.hypot(self.x, self.y)

    def dist(self, other): return (self.sub(other)).len()

    def dot(self, other): return self.x * other.x + self.y * other.y

    def cross(self, other): return self.x * other.y - self.y * other.x

    def cross3(self, p1, p2): return (p1.sub(self)).cross(p2.sub(self))

    def polar(self): return math.atan2(self.y, self.x)


# Basic class for 2D line & segment
class Line2D:
    def __init__(self, _p1: Point2D, _p2: Point2D):
        if _p1.x > _p2.x or (_p1.x == _p2.x and _p1.y > _p2.y):
            (_p1, _p2) = (_p2, _p1)
        self.p1 = _p1
        self.p2 = _p2
        if _p1.x == _p2.x:
            self.a = 1
            self.b = 0
            self.c = -_p1.x
        else:
            self.a = _p2.y - _p1.y
            self.b = _p1.x - _p2.x
            self.c = -(_p1.x * self.a + _p1.y * self.b)
        self.vec = Point2D(self.b, -self.a)

    def get_angle(self, line) -> float:
        p1, p2 = self.vec, line.vec
        cs = max(-1, min(1, p1.dot(p2) / (p1.len() * p2.len())))
        return math.acos(abs(cs))

    def calc(self, x) -> float:
        m, k = -self.a / self.b, -self.c / self.b
        return m * x + k

    def random_point(self) -> Point2D:
        if self.p1.x != self.p2.x:
            x_rnd = random.randrange(int(self.p1.x), int(self.p2.x))
            y_rnd = math.floor(self.p1.y + (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x) * (x_rnd - self.p1.x))
            return Point2D(x_rnd, y_rnd)
        else:
            return Point2D(self.p1.x, random.randrange(int(self.p1.y), int(self.p2.y)))

    def intersect(self, line) -> (bool, Point2D):
        if self.b == 0 and line.b == 0:
            return False, Point2D(0, 0).to_int()
        if self.b != 0 and line.b != 0 and self.a / self.b == line.a / line.b:
            return False, Point2D(0, 0).to_int()

        l1, l2 = copy.deepcopy(self), copy.deepcopy(line)
        if l1.b == 0:
            (l1, l2) = (l2, l1)
        if l2.b == 0:
            return True, Point2D(-l2.c, l1.calc(-l2.c)).to_int()
        x = (l1.b * l2.c - l1.c * l2.b) / (l1.a * l2.b - l1.b * l2.a)
        y = l1.calc(x)
        return True, Point2D(x, y).to_int()


def dot3(p1: Point2D, p2: Point2D, p3: Point2D) -> float:
    return float((p2.sub(p1)).dot((p3.sub(p1))))


# return positive value if counter clock wise, negative value if clock wise, else 0
def ccw(p1: Point2D, p2: Point2D, p3: Point2D) -> float:
    return float(p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y)


# get angle between two vectors (p1 - anchor) and (p2 - anchor)
def get_angle(anchor, p1: Point2D, p2: Point2D) -> float:
    if anchor is not None:
        p1 = p1.sub(anchor)
        p2 = p2.sub(anchor)
    cs = max(-1, min(1, p1.dot(p2) / (p1.len() * p2.len())))
    return math.acos(abs(cs))


# BOJ 17387, return true if two segments are intersect
# https://github.com/justiceHui/icpc-teamnote-for-newbie/blob/master/code/Geometry/SegmentIntersection.cpp
def segment_intersect(l1: Line2D, l2: Line2D) -> bool:
    a, b, c, d = l1.p1, l1.p2, l2.p1, l2.p2
    ab = ccw(a, b, c) * ccw(a, b, d)
    cd = ccw(c, d, a) * ccw(c, d, b)
    if ab == 0 and cd == 0:
        return not (b.less_than(c) or d.less_than(a))
    return ab <= 0 and cd <= 0


# BOJ 11563, return minimum distance between two segments
# https://github.com/justiceHui/icpc-teamnote/blob/master/code/Geometry/SegmentDistance.cpp
def segment_distance(l1: Line2D, l2: Line2D) -> float:
    def _proj(pa: Point2D, pb: Point2D, pc: Point2D) -> float:
        t1, t2 = dot3(pa, pb, pc), dot3(pb, pa, pc)
        if t1 * t2 >= 0 and ccw(pa, pb, pc) != 0:
            return abs(ccw(pa, pb, pc)) / pa.dist(pb)
        else:
            return 1e9

    if segment_intersect(l1, l2):
        return 0.0

    res = 1e9
    a, b = [l1.p1, l1.p2], [l2.p1, l2.p2]
    for i in range(4):
        res = min(res, a[i // 2].dist(b[i % 2]))
    for i in range(2):
        res = min(res, _proj(a[0], a[1], b[i]))
        res = min(res, _proj(b[0], b[1], a[i]))
    return res


# BOJ 1708, get the smallest convex polygon(with some threshold...) contains every points in O(n log n) time.
# https://github.com/justiceHui/icpc-teamnote-for-newbie/blob/master/code/Geometry/ConvexHull.cpp
def convex_hull(points: list[Point2D]) -> list[Point2D]:
    v = copy.deepcopy(points)
    v.sort(key=lambda pt: (pt.x, pt.y))
    lo, hi = [], []
    for p in v:
        while len(lo) >= 2 and (ccw(lo[-2], lo[-1], p) <= 0 or get_angle(p, lo[-2], lo[-1]) < 0.05):
            lo.pop()
        while len(hi) >= 2 and (ccw(hi[-2], hi[-1], p) >= 0 or get_angle(p, hi[-2], hi[-1]) < 0.05):
            hi.pop()
        lo.append(p)
        hi.append(p)
    hi = hi[1:-1]
    return lo + hi[::-1]
