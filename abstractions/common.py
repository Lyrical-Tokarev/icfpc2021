import json
import numpy as np
from collections import defaultdict
import os
from viewer import draw_pair
from shapely.geometry import Polygon, Point
from shapely.geometry import MultiLineString
from tqdm import tqdm

def read_problem(path):
    with open(path) as f:
        data = json.load(f)
    return data

def op(*arrays, operation=np.sum):
    if len(arrays) == 1:
        return arrays[0]
    return [operation(x) for x in zip(*arrays)]


def sums(*arrays):
    return op(*arrays, operation=np.sum)


def means(*arrays):
    return op(*arrays, operation=np.mean)


def get_dist(a, b):
    return np.sum([(x - y) ** 2 for x, y in zip(a, b)])


def plus(a, b):
    return [x + y for x, y in zip(a, b)]


def minus(a, b):
    return [x - y for x, y in zip(a, b)]


def dot(a, b):
    return np.sum([x * y for x, y in zip(a, b)])


def len2(a, b):
    return np.sum([(x-y)**2 for x, y in zip(a, b)])


def length(a):
    return np.sqrt(dot(a, a))


def vector(a, b):
    return minus(b, a)


def mult(a, m):
    return [x * m for x in a]


def norm(a):
    m = length(a)
    return mult(a, 1.0 / m)

def move(points, shift):
    return [plus(p, shift) for p in points]

def perp(a):
    return (-a[1], a[0])


def projection(u, v):
    return dot(u, v)/length(v)

def have_intersection(a, b):
    vect_a = vector(*a)
    vect_b = vector(*b)
    vect_c = vector(a[0], b[0])
    perp_a = perp(vect_a)
    d = dot(perp_a, vect_b)
    if d == 0:
        return False
    n = dot(perp_a, vect_c)
    if n < 0 or n > d:
        return False
    return True
    # return n / d


def validate_distance(v, u, new_v, new_u, epsilon=0):
    old_d = get_dist(v, u)
    new_d = get_dist(new_v, new_u)
    return np.abs(1.*new_d / old_d - 1) <= 1.*epsilon / 1000000.


def get_approximated(figure, new_vertices, epsilon=0):
    neighbors = defaultdict(set)

    for x, y in figure.edges:
        # if x > y:
        neighbors[x].add(y)
        # else:
        neighbors[y].add(x)
    sol = [[np.round(x), np.round(y)] for (x, y) in new_vertices]
    return [sol]

    sequences = []
    for i, (x, y) in enumerate(new_vertices):
        xa, xb = int(np.floor(x)), int(np.ceil(x))
        ya, yb = int(np.floor(y)), int(np.ceil(y))
        variants = [(xa, ya)]
        if ya != yb:
            variants.append((xa, yb))
        if xa != xb:
            variants.append((xb, ya))
            if ya != yb:
                variants.append((xb, yb))
        # print(i, variants)
        if i == 0:
            new_sequences = []
            for v in variants:
                new_sequences.append([v])
            sequences = new_sequences
            continue
        new_sequences = []
        for prefix in sequences:
            for v in variants:
                neigh = [s for s in neighbors[i] if s < i]
                val_results = [
                    validate_distance(
                        figure.vertices[s], figure.vertices[i], prefix[s], v, epsilon=epsilon
                    )
                    for s in neigh
                ] + [True]
                if not np.all(val_results):
                    continue

                new_sequences.append(prefix + [v])
                # print(i, prefix, v, neighbors[i])
        sequences = new_sequences
    return sequences


def get_best_sequences(approx_sequences, figure):
    new_seq = []
    min_dist = None
    for seq in approx_sequences:
        dist = figure.evaluate(seq)
        #dist_data = [np.min([get_dist(p, q) for q in seq]) for p in figure.hole]
        #dist = np.sum(dist_data)
        if min_dist is None or min_dist > dist:
            min_dist = dist
            new_seq = [seq]
        elif dist == min_dist:
            new_seq.append(seq)
    return min_dist, new_seq


def get_best(figure, new_vertices):
    approx_sequences = get_approximated(figure, new_vertices, epsilon=figure.epsilon)
    min_dist, approx_vertices_seqs = get_best_sequences(approx_sequences, figure)
    return approx_vertices_seqs


def save_best_solutions(solutions_dir, problem_id, solutions, figure):
    saved = []

    for i, vertices in enumerate(solutions):
        if not (figure.validate(vertices) and figure.int_validator.check(vertices)):
            continue
        dist = figure.evaluate(vertices)
        path = os.path.join(solutions_dir, str(problem_id), f"geom_{dist}")
        if not os.path.exists(path):
            os.makedirs(path)
        j = len(saved)
        filename = os.path.join(path, f"solution_{j}")
        draw_pair(figure, filename=filename + ".png", new_vert=vertices, distance=dist, show=False)
        with open(filename + ".json", "w") as f:
            json.dump({"vertices": vertices}, f)
        saved.append(i)
    return saved

def move2center(hole, vertices):
    vc = means(*vertices)
    hc = means(*hole)
    shift = vector(vc, hc)
    return move(vertices, shift)


import shapely.affinity as aff
from shapely.ops import polygonize

def shift_points(start_pos, xoffset, yoffset):
    return [[x + xoffset, y + yoffset] for x, y in start_pos]

def rotate_points(start_pos, angle):
    cx, cy = means(*start_pos)
    sin = np.sin(angle)
    cos = np.cos(angle)
    centered = shift_points(start_pos, -cx, -cy)
    centered = [
        [x *cos - y*sin, x*sin + y*cos]
        for x, y in centered
    ]
    return shift_points(centered, cx, cy)

def check_best_angle(figure, start_pos, astep=45, xstep=0.5, ystep=0.5):
    # hole_poly = Polygon(figure.hole)
    ## figure = data['figure']
    ## vertices = figure['vertices']
    ## edges = figure['edges']
    ## epsilon=data['epsilon']
    #figure_shape = MultiLineString(
    #    [(start_pos[s], start_pos[e]) for s, e in figure.edges]
    #)
    np.asarray(figure.hole)
    x0, y0, x1, y1 = figure.get_bounds(figure.hole)
    xf0, yf0, xf1, yf1 = figure.get_bounds(start_pos)
    min_dist = figure.evaluate(start_pos)
    current_pos = start_pos
    for angle in tqdm(np.arange(0, 360, astep)):
        new_pos = rotate_points(start_pos, angle)
        # print("rotation: ", start_pos)
        # print(new_pos, angle)

        # figure_shape1 = aff.rotate(figure_shape, angle=angle)
        #xf0, yf0, xf1, yf1 = figure_shape1.bounds
        xf0, yf0, xf1, yf1 = figure.get_bounds(new_pos)
        new_pos = shift_points(new_pos, -xf0, -yf0)
        #figure_shape1 = aff.translate(figure_shape1, xoff=-xf0, yoff=-yf0)
        xf0, yf0, xf1, yf1 = figure.get_bounds(new_pos)
        xshifts = np.arange(x0-xf0, x1 - xf1+1, xstep)
        yshifts = np.arange(y0-yf0, y1 - yf1+1, ystep)
        # print("shifts:", xshifts, yshifts)
        if len(xshifts) < 1 and len(yshifts) < 1:
            continue
        if len(xshifts) == 0:
            xshifts = [0]
        if len(yshifts) == 0:
            yshifts = [0]
        for xshift in (xshifts):
            for yshift in yshifts:
                f1 = shift_points(new_pos, xshift, yshift)
                xf0, yf0, xf1, yf1 = figure.get_bounds(new_pos)

                # f1 = aff.translate(figure_shape1, xoff=xshift, yoff=yshift)

                # if xf1 > x1 or yf1 > y1:
                #     continue
                # if xf0 < x0 or yf0 < y0:
                #     continue
                if not figure.validate(f1):
                    continue
                # try:
                #     if len(f1.difference(hole_poly)) > 0:
                #         continue
                # except Exception as e:
                #     #print(f1.difference(hole_poly))
                #     #print(e)
                #     continue
                ## try:
                ##     if not check_poly(hole_poly, f1):
                ##         continue
                ## except:
                ##     continue

                # vert_info = { i: point
                #         for v, edge in zip(f1.geoms, figure.edges)
                #         for i, point in list(zip(edge, v.coords))
                # }
                # new_vertices = [
                #     list(vert_info[k])
                #     for k in sorted(vert_info)
                # ]
                # if not figure.validate(new_vertices):
                #     continue
                new_dist = figure.evaluate(f1)
                if new_dist < min_dist and figure.validate(f1):
                    min_dist = new_dist
                    current_pos = f1
                # figure_shape = MultiLineString([(vertices[s], vertices[e]) for s, e in edges])
                # return new_vertices
                # return dist, xshift, yshift, angle, f1
        print("rotation", angle, min_dist)

    return current_pos

if __name__ == "__main__":
    # some checks
    print(sums([1, 1]))
    print(sums([1, 1], [3, 3]))
    print(means([1, 1]))
    print(means([1, 1], [3, 3]))
