import requests
import json

base = "http://localhost:8000"

# 1. Login
login_res = requests.post(f"{base}/auth/login", json={
    "email": "student@demo.com",
    "password": "password" # we don't know the password... let's use the instructor to test
})

print("Login status:", login_res.status_code)
if login_res.status_code == 401:
    print("Trying instructor credentials...")
    login_res = requests.post(f"{base}/auth/login", json={
        "email": "demo-instructor@example.edu",
        "password": "Demo1234!"
    })
    print("Instructor Login status:", login_res.status_code)

if login_res.status_code != 200:
    print("Failed to login", login_res.text)
    exit(1)

token = login_res.json()["access_token"]
print("Token:", token[:20] + "...")

# 2. Get next activity
print("Hitting /activities/next...")
res = requests.get(
    f"{base}/activities/next",
    headers={"Authorization": f"Bearer {token}"}
)
print("Status:", res.status_code)
if res.status_code == 200:
    print(json.dumps(res.json(), indent=2))
else:
    print(res.text)
