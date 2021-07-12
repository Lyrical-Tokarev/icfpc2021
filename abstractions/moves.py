"""
Random manipulations with figure
"""
import numpy as np
from common import *
import networkx as nx

def flip_points(current_vertices, i, j, points=[]):
    assert len(points) > 0
    new_vertices = [[x, y] for x, y in current_vertices]
    if len(points) == 0:
        return new_vertices
    a = current_vertices[i]
    b = current_vertices[j]
    print(i, j, points)
    v0 = norm(vector(a, b))
    for k in points:
        c = current_vertices[k]
        u = vector(a, c)
        p = mult(v0, projection(u, v0))

        n = sums(mult(p, -1), u)
        new_pos = sums(a, sums(mult(n, -1), p))
        new_vertices[k] = new_pos
    return new_vertices


class MovePoint:
    def __init__(self, figure):
        self.figure = figure

    @property
    def is_useful(self):
        return True

    def __call__(self, vertices, edges):
        pass


class FlipEar:
    def __init__(self, figure):
        self.figure = figure
        # self.vertices = vertices
        # self.edges = edges
        self.ears = [s for s, n in self.figure.neighbors.items() if len(n) == 2]

    @property
    def is_useful(self):
        return len(self.ears) > 0

    def __call__(self, current_vertices):
        e = np.random.choice(self.ears)
        # todo: flip point
        i, j = list(self.figure.neighbors[e])
        return flip_points(current_vertices, i, j, points=[e])


class RotateSplitPoint:
    def __init__(self, figure):
        pass

    def is_useful(self):
        pass

    def __call__(self):
        pass


class Flip2Points:
    def __init__(self, figure):
        #print("11")
        # self.vertices = vertices
        # self.edges = edges
        # self.epsilon = epsilon
        self.figure = figure
        n = len(figure.vertices)
        # g = nx.Graph()
        # for i in np.arange(n):
        #     g.add_node(i)
        # for i, j in figure.edges:
        #     g.add_edges(figure.edges)
        self.pairs = dict()
        # assert np.unique(g.clusters(mode="weak").membership).shape[0] <= 1

        # print(n, vertices)
        for i in range(n - 1):
            for j in range(i + 1, n):
                # print(i, j)
                g = nx.Graph()
                for k in np.arange(n):
                    g.add_node(k)
                # g.add_vertices(n)
                sel_edges = [
                    (x, y)
                    for x, y in figure.edges if x != i and x!=j and y!=i and y!=j
                ]
                # print(edges)
                # if len(sel_edges) < 1:
                #     continue
                # print(sel_edges)
                for x, y in sel_edges:
                    g.add_edge(x, y)
                components = list(nx.connected_components(g))
                #print(i, j, components)
                components = [
                    [c for c in comp if c != i and c!=j]
                    for comp in components]
                components = [c for c in components if len(c) > 0]
                #print(components)
                # g.add_edges(sel_edges)
                # clusters = g.clusters(mode="weak")
                # c = components.membership[i]
                # components = defaultdict(set)
                # print(clusters.membership)
                # for k, c in zip(range(n), clusters.membership):
                #     if k != i and k != j:
                #         components[c].add(k)
                # print(components)
                # components = [list(c) for c in components.values()]
                # print(components)
                if len(components) > 1:
                    self.pairs[(i, j)] = components
                    self.pairs[(j, i)] = components

    @property
    def is_useful(self):
        return len(self.pairs) > 0

    def __call__(self, current_vertices, randomize=True):
        n = len(self.pairs)
        arr = list(self.pairs)
        if randomize:
            i, j = arr[np.random.choice(n)]
            sep = self.pairs[(i, j)]
            sep = sep[np.random.choice(len(sep))]
            # print(i, j, sep)
            # todo: flip point
            return flip_points(current_vertices, i, j, points=sep)
        total = []
        for (i, j), comp in self.pairs.items():
            sep = sep = np.random.choice(comp)
            total.append(flip_points(current_vertices, i, j, points=sep))
        return total


def mc_opt(figure, start_pos, n_iterations=100, moves=[], prob=0.1):
    current_pos = start_pos
    candidates = []
    for i in range(n_iterations):
        new_candidates = []
        for pos in candidates:
            move = np.random.choice(moves)
            moved = move(pos)
            new_candidates.append(moved)
        candidates = new_candidates
    pass
