"""Script for running optimization block
"""
import sys
import os
sys.path.append("abstractions")
from common import read_problem
from entities import Figure
from forces import optimize_positions


if __name__=="__main__":
    problem_id = 23
    path = os.path.join("data", f"problem_{problem_id}.json")
    data = read_problem(path)
    figure = Figure(data)
    current_pos = data['figure']['vertices']
    magnets = {
        0 : [0], 
        1: [5],
        2: [4],
        3: [1],
        4: [3],
        5: [2]
    }
    optimize_positions(figure, current_pos, n_iterations=100, magnets=magnets)