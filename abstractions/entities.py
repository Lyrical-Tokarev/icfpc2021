"""
basic abstractions: player's figure, hole and so on.
"""
import numpy as np
from scipy.spatial import Delaunay

from common import *


class Validator:
    def check(self, vertices):
        return True


class IntValidator(Validator):
    def __init__(self):
        pass

    def check(self, new_vertices):
        results = [(x.is_integer() if isinstance(x, float) else isinstance(x, int)) for xs in new_vertices for x in xs]
        return np.all(results)

    # def check(self, edges, vertices, hole, epsilon):
    #     # all coordinates should be int values
    #     pass


class PlacementValidator(Validator):
    def __init__(self, edges, hole):
        self.edges = edges
        self.hole = hole
        self.triangulated_hole = Delaunay(hole)

    def check(self, new_vertices):
        # 1. test that all points are inside
        results = self.triangulated_hole.find_simplex(new_vertices)
        for r in results:
            if r < 0:
                return False
        # 2. test for line intersection
        for x, y in zip(self.hole, np.roll(self.hole, -1)):
            for i, j in self.edges:
                a = new_vertices[i]
                b = new_vertices[j]
            if have_intersection([x, y], [a, b]):
                return False
        return True


class EdgesValidator(Validator):
    def __init__(self, edges, vertices, hole, epsilon):
        self.edges = edges
        self.hole = hole
        self.epsilon = epsilon
        self.vertices = vertices
        pos = [(vertices[i], vertices[j]) for i, j in edges]
        self.dist = [get_dist(x, y) for x, y in pos]

    def check(self, new_vertices):
        assert len(self.vertices) == len(new_vertices)
        new_dist = [get_dist(new_vertices[i], new_vertices[j]) for i, j in self.edges]
        conditions = [
            np.abs(dn / do - 1) <= self.epsilon / 10 ** 6
            for dn, do in zip(new_dist, self.dist)
        ]
        return np.all(conditions)


class Fold:
    def __init__(self, folded_dict, figure=None):
        self.coords = list(folded_dict)
        self.groups = [folded_dict[c] for c in self.coords]
        self.n = np.max(self.groups) + 1
        self.figure = figure

    def unfold(self, vertices):
        assert self.groups == len(vertices)
        coords = [(i, vertices[i]) for group in self.groups for i in group]
        coords = [v for (i, v) in sorted(coords, key=lambda x: x[0])]

        return coords


class Figure:
    def __init__(self, data):
        figure = data["figure"]
        self.edges = figure["edges"]
        self.vertices = figure["vertices"]
        self.hole = data["hole"]
        self.epsilon = data["epsilon"]
        self.validators = [
            # IntValidator(),
            PlacementValidator(self.edges, self.hole),
            EdgesValidator(self.edges, self.vertices, self.hole, self.epsilon),
        ]
        self.int_validator = IntValidator()
        self.neighbors = defaultdict(set)
        for s, e in self.edges:
            self.neighbors[s].add(e)
            self.neighbors[e].add(s)

    def get_bounds(self, points):
        xs = [x for x, y in points]
        ys = [y for x, y in points]
        bounds = [np.min(xs), np.min(ys), np.max(xs), np.max(ys)]
        return bounds
    def validate(self, new_vertices):
        results = [v.check(new_vertices) for v in self.validators]
        return np.all(results)

    def compute_edge_diff(self, new_pos, s, e):
        a, b = new_pos[s], new_pos[e]
        x, y = self.vertices[s], self.vertices[e]
        do = len2(x, y)
        dn = len2(a, b)
        return dn, do

    def evaluate(self, new_vertices):
        """Computes metric for figure's coordinates
        """
        distances = [np.min([get_dist(h, v) for v in new_vertices]) for h in self.hole]
        return np.sum(distances)

    def make_fold(self, vertices):
        folded_dict = defaultdict(list)
        for i, (x, y) in enumerate(vertices):
            folded_dict[(x, y)].append(i)
        return Fold(folded_dict)


class FoldedFigure(Figure):
    """
    """

    def __init__(self, figure, fold):
        self.figure = figure
        self.fold = fold

    def evaluate(self, new_vertices):
        vertices = self.fold.unfold(new_vertices)
        return self.figure.evaluate(vertices)

    def validate(self, new_vertices):
        vertices = self.fold.unfold(new_vertices)
        return self.figure.validate(vertices)
