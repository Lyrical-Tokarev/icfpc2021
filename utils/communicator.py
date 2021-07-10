import os
import requests
import json
import sys


class Communicator:
    def __init__(self, base_url="https://poses.live"):
        self.base_url = base_url

    def get_hello(self):
        api_key = os.getenv("POSES_API_KEY", None)
        url = f"{self.base_url}/api/hello"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        return response.json()

    def get_problem(self, problem_id=0):
        api_key = os.getenv("POSES_API_KEY", None)
        url = f"{self.base_url}/api/problems/{problem_id}"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        if not response.ok:
            return None
        return response.json()

    def post_problem(self, problem_id, data={}):
        api_key = os.getenv("POSES_API_KEY", None)
        url = f"{self.base_url}/api/problems/{problem_id}/solutions"
        if len(data) == 0:
            print("provide some data next time")
            return None
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json=data
        )
        return response.ok, response.text


if __name__ == "__main__":
    """
    Sample call (from repo's main dir):

    python utils/communicator.py problems 1 60
    """
    print(sys.argv)
    communicator = Communicator()
    response = communicator.get_hello()
    print("Hello result:", response)
    target_dir = sys.argv[1]
    start = int(sys.argv[2])
    end = int(sys.argv[3])
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for problem_id in range(start, end):
        data = communicator.get_problem(problem_id)
        if data is None:
            print("Problem_id=", problem_id, " - not available")
            continue
        path = os.path.join(target_dir, "problem_"+ str(problem_id) + ".json")
        # if not os.path.exists(path):
        #     os.makedirs(path)
        # path = os.path.join(path, "problem.json")
        with open(path, 'w') as f:
            f.write(json.dumps(data))
