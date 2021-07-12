"""Force-directed graph layouting-related stuff
https://en.wikipedia.org/wiki/Force-directed_graph_drawing
"""
from collections import defaultdict
import numpy as np

from common import *


def compute_forces(
    figure, current_pos, # orig_edges, targets, sources, epsilon,
    magnets=dict()
):
    sources = figure.vertices
    forces = defaultdict(list)
    # center force
    #     if len(magnets) == 0:
    #         z = means(current_pos)
    #         for i, x in enumerate(current_pos):
    #             forces[i].append(mult(vect(z, x), 0.1))

    for src, tgts in magnets.items():
        u = current_pos[src]
        for t in tgts:
            v = figure.hole[t]
            d = vector(u, v)
            # print(src, tgts, length(d))
            if length(d) < 10:  # and len(tgts)==1: # was 1 condition
                m = 1.0
            elif length(d) < 1:
                m = 0
            else:
                m = 0.5  # was:0.5
            forces[src].append(mult(d, m))
    for s, e in figure.edges:
        dn, do = figure.compute_edge_diff(current_pos, s, e)
        edge_diff = dn/do-1
        a, b = current_pos[s], current_pos[e]
        # u, v = sources[s], sources[e]
        # dn = len2(vect(a, b))
        # do = len2(vect(u, v))
        # if (dn - do)*1000000 >= epsilon*do: # dn/do-1 >= epsilon/1000000:
        #     direction = 1*(np.sqrt(dn) - np.sqrt(do))
        # elif (dn - do)*1000000 <= - epsilon*do:
        #     direction = -1*(np.sqrt(do) - np.sqrt(dn))
        # else:
        #     direction = 0.01
        if edge_diff >= figure.epsilon / 10 ** 6:
            direction = 1 * (np.sqrt(dn) - np.sqrt(do))
        elif edge_diff <= - figure.epsilon / 10 ** 6:
            direction = -1 * (np.sqrt(do) - np.sqrt(dn))
        else:
            direction = 0.01
        if direction > 0:
            if not s in magnets or len(magnets[s]) > 1:
                forces[s].append(mult(vector(a, b), direction))
            if not e in magnets or len(magnets[e]) > 1:
                forces[e].append(mult(vector(b, a), direction))
    for k in range(len(sources)):
        if k not in forces:
            forces[k].append((0, 0))
    return forces


def modify_pos(pos, delta, forces, verbose=True):
    force = means(*forces)
    if verbose:
        print(forces)
        print(pos, force)

    # print(pos, delta, force)
    # print([(p,f) for p, f in zip(pos, force)])
    return [(p + f * delta) for p, f in zip(pos, force)]


def optimize_positions(figure, current_pos, n_iterations=100, magnets=dict(), delta=0.1,
        solutions_dir="solutions_new", problem_id=0, save=True):
    n = len(current_pos)
    magnets_ = magnets
    for k in range(n_iterations):
        if k > 40:
            magnets_ = {}#{k: v for k, v in magnets.items() if len(v) == 1}
        # if k > 70:
        #    magnets_= dict()
        forces = compute_forces(
            figure, current_pos, #  orig_edges, targets, sources, epsilon,
            magnets=magnets_
        )
        current_pos = [modify_pos(current_pos[i], delta, forces[i]) for i in range(n)]
        print("current_pos", current_pos)
        solutions = get_best(figure, current_pos)
        print("sol:", solutions)
        # print(current_pos)
        if save:
            save_best_solutions(solutions_dir, problem_id, solutions, figure)
        # figure_shape = MultiLineString(
        #     [(current_pos[s], current_pos[e]) for s, e in edges]
        # )
        #
        # # if i%2==0:
        # draw_pair(
        #     hole_poly, figure_shape, filename=None, label=str(i), new_vert=current_pos
        # )
    return solutions
