"""
basic abstractions: player's figure, hole and so on.
"""
import numpy as np
from scipy.spatial import Delaunay

from .common import *


class Validator:
    def check(self, vertices):
        return True


class IntValidator(Validator):
    def __init__(self):
        pass

    def check(self, new_vertices):
        results = [x.is_integer() for xs in new_vertices for x in xs]
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
        for x, y in zip(hole, np.roll(hole, -1)):
            



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
            dn / do <= epsilon / 10 ** 6 for dn, do in zip(new_dist, self.dist)
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
            IntValidator(),
            PlacementValidator(self.edges, self.hole),
            EdgesValidator(self.edges, self.vertices, self.hole, self.epsilon),
        ]

    def validate(self, new_vertices):
        results = [v.check(v) for v in self.validators]
        return np.all(results)

    def evaluate(self, new_vertices):
        """Computes metric for figure's coordinates
        """
        distances = [np.min([get_dist(h, v) for v in new_vertices]) for h in hole]
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
