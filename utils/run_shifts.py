"""
Script which shifts image and occationally deforms the figure
"""
import sys
import os
from collections import defaultdict
import numpy as np
sys.path.append("abstractions")
from common import read_problem
from entities import Figure
from forces import optimize_positions


if __name__=="__main__":
    for problem_id in np.arange(24, 34):
        path = os.path.join("data", f"problem_{problem_id}.json")
        data = read_problem(path)
        figure = Figure(data)
        current_pos = data['figure']['vertices']
        # magnets = {
        #     0 : [0],
        #     1: [5],
        #     2: [4],
        #     3: [1],
        #     4: [3],
        #     5: [2]
        # }
        n = len(figure.hole)
        magnets = defaultdict(list)
        for i in range(n):
            k = np.random.choice(len(figure.vertices))
            magnets[k].append(i)

        print(figure.vertices, figure.hole)
        #for seed in np.arange(10):
        #    np.random.seed(seed)
        # optimize_positions(figure, current_pos, n_iterations=100, magnets=magnets,
        #     solutions_dir="solutions_new", problem_id=problem_id)
        check_best_angle(
            figure, current_pos, astep=45, xstep=0.5, ystep=0.5,
            solutions_dir="solutions_new", problem_id=problem_id
        )
