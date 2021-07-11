"""Force-directed graph layouting-related stuff
https://en.wikipedia.org/wiki/Force-directed_graph_drawing
"""
from collections import defaultdict
import numpy as np

from common import *


def compute_forces(current_pos, orig_edges, targets, sources, epsilon, magnets=dict()):
    forces = defaultdict(list)
    # center force
#     if len(magnets) == 0:
#         z = means(current_pos)
#         for i, x in enumerate(current_pos):
#             forces[i].append(mult(vect(z, x), 0.1))
        
    for src, tgts in magnets.items():
        u = current_pos[src]
        for t in tgts:
            v = targets[t]
            d = vect(u, v)
            #print(src, tgts, length(d))
            if length(d) < 10:# and len(tgts)==1: # was 1 condition
                m = 1.
            elif length(d) < 1:
                m = 0
            else:
                m = 0.5 # was:0.5
            forces[src].append(mult(d, m))
    for s, e in orig_edges:
        a, b = current_pos[s], current_pos[e]
        u, v = sources[s], sources[e]
        dn = len2(vect(a, b))
        do = len2(vect(u, v))
        if (dn - do)*1000000 >= epsilon*do: # dn/do-1 >= epsilon/1000000:
            direction = 1*(np.sqrt(dn)-np.sqrt(do))
        elif (dn - do)*1000000 <= - epsilon*do:
            direction = -1*(np.sqrt(do)-np.sqrt(dn))
        else:
            direction = 0.01
        if direction > 0:
            if not s in magnets or len(magnets[s])>1:
                forces[s].append(mult(vect(a, b), direction))
            if not e in magnets or len(magnets[e])>1:
                forces[e].append(mult(vect(b, a), direction))
    for k in range(len(sources)):
        if k not in forces:
            forces[k].append((0, 0))
    return forces


def modify_pos(pos, delta, forces, verbose=True):
    force = means(*forces)
    if verbose:
        print(forces)
        print(pos, force)
    
    #print(pos, delta, force)
    #print([(p,f) for p, f in zip(pos, force)])
    return [ (p + f*delta) for p, f in zip(pos, force)]