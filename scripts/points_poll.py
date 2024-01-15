import requests


def reward():
    r = requests.post(f"http://localhost:5000/api/v1/referral/users/poll_points")
    print(f"Poll points request: {r.ok}")
    if not r.ok:
        print(r.text)
    return r.ok


if __name__ == '__main__':
    reward()
