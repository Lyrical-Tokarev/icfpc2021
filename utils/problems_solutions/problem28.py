"""Script for running optimization block
"""
import sys
import os
from collections import defaultdict
import numpy as np
sys.path.append("abstractions")
from common import read_problem, move2center, check_best_angle, get_best, save_best_solutions, get_dist
from entities import Figure
from forces import optimize_positions
from moves import Flip2Points
from viewer import draw_pair
import matplotlib.pyplot as plt


if __name__=="__main__":
    solved_problems = []
    for problem_id in np.arange(60, 80):
        path = os.path.join("data", f"problem_{problem_id}.json")
        data = read_problem(path)
        figure = Figure(data)
        #if len(figure.hole) > 10 or len(figure.vertices) > 10:
        #    continue
        current_pos = data['figure']['vertices']
        n = len(figure.hole)
        # magnets = defaultdict(list)
        # for i in range(n):
        #     k = np.random.choice(len(figure.vertices))
        #     magnets[k].append(i)
        f2p = Flip2Points(figure)

        print("figure:", figure.vertices, figure.hole)
        #for seed in np.arange(10):
        #    np.random.seed(seed)
        if not f2p.is_useful:
            print("f2p not useful")
            continue
        current_pos = move2center(figure.hole, current_pos)
        # current_pos = check_best_angle(figure, current_pos, astep=5, xstep=0.5, ystep=0.5)

        new_pos = f2p(current_pos, randomize=True)
        print("current", current_pos)
        print(new_pos)
        current_pos = new_pos
        dirname = os.path.join("solutions_new", str(problem_id))
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        filename = os.path.join("solutions_new", str(problem_id), f"current")
        draw_pair(figure, filename=filename + ".png", new_vert=new_pos, distance=figure.evaluate(new_pos), show=False)
        plt.close('all')

        #distance = figure.evaluate(new_pos) # for pos in new_pos]

        #if distance > figure.evaluate(current_pos):
        #    continue
        print("have current_pos")
        try:
            pos = new_pos
            #pos = check_best_angle(figure, pos, astep=5, xstep=0.2, ystep=0.2)


            magnets = dict()
            for i, a in enumerate(figure.hole):
                distances = [get_dist(a, b) for b in new_pos]
                mdist = np.min(distances)
                magnets[i] = np.where(distances == mdist)[0]
            #print(magnets)

            #positions = optimize_positions(figure, pos, n_iterations=2, magnets=magnets,
            #solutions_dir="solutions_new", problem_id=problem_id)
            #print(positions)
            #break
            #for pos in new_pos:
            # print("pos before", pos)
            #if figure.evaluate(current_pos) < figure.evaluate(pos) and figure.valid(new_pos):
            print(pos)
            pos = check_best_angle(figure, pos, astep=45, xstep=0.5, ystep=0.5)
            if pos is None:
                print("check best angle failed")
                continue
            print("pos", pos)
            solutions = get_best(figure, pos)
            print("sol:", solutions)
            # print(current_pos)

            dist = [figure.evaluate(s)for s in solutions]
            i = np.argmin(dist)
            new_pos = solutions[i]
            if figure.validate(new_pos) and figure.int_validator(new_pos):
                current_pos = new_pos
            save_best_solutions("solutions_new", problem_id, solutions, figure)

            filename = os.path.join("solutions_new", str(problem_id), f"current")
            draw_pair(figure, filename=filename + ".png", new_vert=new_pos, distance=figure.evaluate(current_pos), show=False)
            plt.close('all')

            # optimize_positions(figure, pos, n_iterations=100, magnets=magnets,
            #     solutions_dir="solutions_new", problem_id=problem_id)
        except Exception as e:
            print(e)
            continue
    #solved_problems.append(problem_id)


    print(solved_problems)
