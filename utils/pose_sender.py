"""
Script for sending all solved puzzles to server
"""
import click
import json
import os
import sys
import numpy as np

print("cwd=", os.getcwd())
sys.path.append("abstractions")
from entities import Figure
from communicator import Communicator


def read_submission_result(sol_dir):
    "checks if there is file status.json in the solution directory and returns its contents"
    path = os.path.join(sol_dir, "status.json")
    if not os.path.exists(path):
        return
    with open(path) as f:
        data = json.load(f)
    return data


def get_pose_id(sol_dir):
    "checks if there is file pose_info.json in the solution dir"
    path = os.path.join(sol_dir, "pose_info.json")
    if not os.path.exists(path):
        return
    with open(path) as f:
        data = json.load(f)
    return data["pose_id"]


def save_submission_status(sol_dir, pose_info):
    path = os.path.join(sol_dir, "status.json")
    with open(path, "w") as f:
        json.dump(pose_info, f)


def get_submission_status(communicator, problem_id, pose_id):
    data = communicator.get_pose_status(problem_id=problem_id, pose_id=pose_id)
    return data
    pass


def get_valid_solution(sol_dir, problem_path):
    candidates = [
        x for x in os.listdir(sol_dir) if x.startswith("solution") and x[-5:] == ".json"
    ]
    valid_path = None
    with open(problem_path) as f:
        problem = json.load(f)
    figure = Figure(problem)

    for filename in candidates:
        path = os.path.join(sol_dir, filename)
        with open(path) as f:
            data = json.load(f)
        if figure.validate(data['vertices']):
            valid_path = path
            break
    return valid_path


def send_solution(communicator, problem_id, path):
    with open(path) as f:
        data = json.load(f)
    status, text = communicator.post_problem(problem_id, data=data)
    directory = os.path.dirname(path)
    status_path = os.path.join(directory, "pose_info.json")
    data["pose_id"] = text
    data["path"] = path
    with open(status_path, "w") as f:
        json.dump(data, f)
    return text


@click.command()
@click.argument("start", type=int)  # help="start puzzle id",
@click.argument("end", type=int)  # help="end puzzle id",
@click.option(
    "--solution_dir",
    default="solutions_new",
    help="directory with solutions to check (writable)",
)
@click.option(
    "--problem_dir", default="data", help="directory with solutions to check (writable)"
)
@click.option("--verbose", default=False)
def check_and_send(start, end, solution_dir, problem_dir, verbose):
    # iterate over solution directories
    # find valid solution with best score
    # if it has file with pose_id and status, ignore it
    # if there is no status - check status, save to file and go to next pose
    # if there is no pose_id file, send it to the server, save pose_id to file
    if not os.path.exists(solution_dir):
        print(f"{solution_dir} doesn't exist, exiting")
        return
    communicator = Communicator()
    print("starting", start, end)
    for i in range(start, end + 1):
        data_dir = os.path.join(solution_dir, str(i))
        if not os.path.exists(data_dir):
            continue
        try:
            solutions = sorted(
                [x for x in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, x))],
                key=lambda x: int(np.round(np.float(x.split("_")[1]))))
        except Exception as e:
            print(e)
            print(data_dir, os.listdir(data_dir))
        solutions = [os.path.join(data_dir, x) for x in solutions]
        for sol_dir in solutions:
            result = read_submission_result(sol_dir)
            if result is not None:
                print(result)
                if verbose:
                    print(f"Problem {i} was solved previosly, result=", result)
                if result["state"] == "VALID":
                    break
                if result["state"] == "INVALID":
                    continue
            pose_id = get_pose_id(sol_dir)
            if pose_id is not None:
                result = get_submission_status(communicator, i, pose_id)
                if result is not None:
                    save_submission_status(sol_dir, result)
                print(f"Problem {i} was solved, current status=", result)
                break
            problem_path = os.path.join(problem_dir, f"problem_{i}.json")
            path = get_valid_solution(sol_dir, problem_path)
            if path is not None:
                pose_id = send_solution(communicator, i, path)
                break
    pass


if __name__ == "__main__":
    check_and_send()
