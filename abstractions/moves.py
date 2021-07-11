"""
Random manipulations with figure
"""
import numpy as np


def flip_points(current_vertices, i, j, points=[]):
    new_vertices = [[x, y] for x, y in current_vertices]
    if len(points) == 0:
        return new_vertices
    a = current_vertices[i]
    b = current_vertices[j]
    v0 = norm(vect(a, b))
    for k in points:
        c = current_vertices[k]
        u = vect(a, c)
        p = mult(v0, projection(u, v0))

        n = vsum(mult(p, -1), u)
        new_pos = vsum(a, vsum(mult(n, -1), p))
        new_vertices[k] = new_pos
    return new_vertices[k]


class MovePoint:
    def __init__(self, vertices, edges, epsilon=0):
        self.vertices = vertices
        self.edges = edges
        self.epsilon = epsilon

    @property
    def is_useful(self):
        return True

    def __call__(self, vertices, edges):
        pass


class FlipEar:
    def __init__(self, vertices, edges, epsilon=0):
        self.vertices = vertices
        self.edges = edges
        self.neighbors = defaultdict(set)
        for s, e in edges:
            self.neighbors[s].add(e)
            self.neighbors[e].add(s)
        self.ears = [s for s, n in self.neighbors.items() if len(n) == 2]
        pass

    @property
    def is_useful(self):
        return len(self.ears) > 0

    def __call__(self, current_vertices):
        e = np.random.choice(self.ears)
        # todo: flip point
        i, j = list(self.neighbors[e])
        return flip_points(current_vertices, i, j, points=[e])


class RotateSplitPoint:
    def __init__(self, vertices, edges, epsilon=0):
        pass

    def is_useful(self):
        pass

    def __call__(self):
        pass


class Flip2Points:
    def __init__(self, vertices, edges, epsilon=0):
        print("11")
        self.vertices = vertices
        self.edges = edges
        self.epsilon = epsilon
        n = len(vertices)
        g = Graph()
        g.add_vertices(n)
        g.add_edges(edges)
        self.pairs = dict()
        assert np.unique(g.clusters(mode="weak").membership).shape[0] <= 1

        # print(n, vertices)
        for i in range(n - 1):
            for j in range(i + 1, n):
                # print(i, j)
                g = Graph()
                g.add_vertices(n)
                sel_edges = [
                    (x, y) for x, y in edges if x not in (i, j) and y not in (i, j)
                ]
                # print(edges)
                if len(sel_edges) < 1:
                    continue
                # print(sel_edges)
                g.add_edges(sel_edges)
                clusters = g.clusters(mode="weak")
                # c = components.membership[i]
                components = defaultdict(set)
                for k, c in zip(range(n), clusters.membership):
                    components[c].add(k)
                components = [list(c) for c in components.values()]
                if len(components) > 1:
                    self.pairs[(i, j)] = components
                    self.pairs[(j, i)] = components

    @property
    def is_useful(self):
        return len(self.pairs) > 0

    def __call__(self, current_vertices):
        i, j = np.random.choice(self.pairs)
        sep = np.random.choice(self.pairs[(i, j)])
        # todo: flip point
        return flip_points(current_vertices, i, j, points=sep)


def mc_opt(edges, vertices, hole, moves=[], prob=0.1):
    pass
