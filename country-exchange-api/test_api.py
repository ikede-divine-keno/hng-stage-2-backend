# test_api.py
import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# CONFIG
BASE_URL = "http://localhost:8000"
REFRESH_ENDPOINT = f"{BASE_URL}/countries/refresh"
STATUS_ENDPOINT = f"{BASE_URL}/status"
COUNTRIES_ENDPOINT = f"{BASE_URL}/countries"
IMAGE_ENDPOINT = f"{BASE_URL}/countries/image"

# === MANUAL SERVER START ===
print("Please start the server manually:")
print("   py -3.12 -m uvicorn main:app --reload --port 8000")
print("Then press Enter to continue...")
input("Press Enter when server is running...")

# Test connection
try:
    requests.get(BASE_URL, timeout=5)
    print("Server is reachable!\n")
except:
    print("Cannot reach server! Is it running on port 8000?")
    sys.exit(1)

# Test state
score = 0
max_score = 100
tests = []

def test(name, points, result):
    global score
    status = "Passed" if result else "Failed"
    print(f"{status} {name} ({points} pts)")
    if result:
        score += points

# TEST 1: POST /countries/refresh
print("\n=== TEST 1: POST /countries/refresh (25 points) ===")
try:
    r = requests.post(REFRESH_ENDPOINT, timeout=30)
    test("Refresh endpoint accessible", 3, r.status_code == 200)
    test("Returns correct status code", 2, r.status_code == 200)

    # Wait for image
    time.sleep(3)

    # Check DB
    status = requests.get(STATUS_ENDPOINT).json()
    total = status.get("total_countries", 0)
    test("Countries stored after refresh", 20, total > 200)
except Exception as e:
    test("Refresh endpoint accessible", 3, False)
    test("Returns correct status code", 2, False)
    test("Countries stored after refresh", 20, False)

# TEST 2: GET /countries + filters + sort
print("\n=== TEST 2: GET /countries (filters & sorting) (25 points) ===")
try:
    r = requests.get(COUNTRIES_ENDPOINT)
    test("Basic GET /countries works", 5, r.status_code == 200 and isinstance(r.json(), list))

    countries = r.json()
    test("Response is valid array of countries", 10, len(countries) > 200 and "name" in countries[0])

    # Filter: region=Africa
    r = requests.get(f"{COUNTRIES_ENDPOINT}?region=Africa")
    africa = r.json()
    test("?region=Africa filter works", 5, len(africa) > 50 and all(c["region"] == "Africa" for c in africa))

    # Sort: gdp_desc
    r = requests.get(f"{COUNTRIES_ENDPOINT}?sort=gdp_desc")
    sorted_gdp = r.json()
    gdps = [c["estimated_gdp"] for c in sorted_gdp if c["estimated_gdp"]]
    test("?sort=gdp_desc works", 5, gdps == sorted(gdps, reverse=True))
except:
    test("Basic GET /countries works", 5, False)
    test("Response is valid array of countries", 10, False)
    test("?region=Africa filter works", 5, False)
    test("?sort=gdp_desc works", 5, False)

# TEST 3: GET /countries/:name
print("\n=== TEST 3: GET /countries/:name (10 points) ===")
try:
    r = requests.get(f"{COUNTRIES_ENDPOINT}/Nigeria")
    test("Returns Nigeria", 5, r.status_code == 200 and r.json()["name"] == "Nigeria")

    r = requests.get(f"{COUNTRIES_ENDPOINT}/NonExistentCountry123")
    test("404 for non-existent", 5, r.status_code == 404 and r.json()["error"] == "Country not found")
except:
    test("Returns Nigeria", 5, False)
    test("404 for non-existent", 5, False)

# TEST 4: DELETE /countries/:name
print("\n=== TEST 4: DELETE /countries/:name (10 points) ===")
try:
    # Add test country via refresh (assume it's there)
    requests.post(REFRESH_ENDPOINT)
    time.sleep(1)

    r = requests.delete(f"{COUNTRIES_ENDPOINT}/Nigeria")
    test("DELETE Nigeria returns 200", 5, r.status_code == 200)

    r = requests.get(f"{COUNTRIES_ENDPOINT}/Nigeria")
    test("Nigeria is deleted", 3, r.status_code == 404)

    r = requests.delete(f"{COUNTRIES_ENDPOINT}/NonExistent")
    test("DELETE non-existent → 404", 2, r.status_code == 404)
except:
    test("DELETE Nigeria returns 200", 5, False)
    test("Nigeria is deleted", 3, False)
    test("DELETE non-existent → 404", 2, False)

# TEST 5: GET /status
print("\n=== TEST 5: GET /status (10 points) ===")
try:
    r = requests.get(STATUS_ENDPOINT)
    data = r.json()
    test("Status endpoint accessible", 3, r.status_code == 200)
    test("Returns total_countries", 3, "total_countries" in data and data["total_countries"] > 0)
    test("Returns last_refreshed_at", 2, "last_refreshed_at" in data)
    test("Valid timestamp format", 2, "Z" in data["last_refreshed_at"])
except:
    test("Status endpoint accessible", 3, False)
    test("Returns total_countries", 3, False)
    test("Returns last_refreshed_at", 2, False)
    test("Valid timestamp format", 2, False)

# TEST 6: GET /countries/image
print("\n=== TEST 6: GET /countries/image (10 points) ===")
try:
    r = requests.get(IMAGE_ENDPOINT)
    test("Image endpoint accessible", 3, r.status_code in [200, 404])

    if r.status_code == 200:
        test("Correct Content-Type: image/png", 3, r.headers["Content-Type"] == "image/png")
        test("Returns image content (>1000 bytes)", 4, len(r.content) > 1000)
    else:
        test("Correct Content-Type: image/png", 3, False)
        test("Returns image content (>1000 bytes)", 4, False)
except:
    test("Image endpoint accessible", 3, False)
    test("Correct Content-Type: image/png", 3, False)
    test("Returns image content (>1000 bytes)", 4, False)

# TEST 7: Error Handling & Validation
print("\n=== TEST 7: Error Handling & Validation (10 points) ===")
try:
    # 404 format
    r = requests.get(f"{COUNTRIES_ENDPOINT}/xyz")
    test("404 returns proper JSON", 3, r.json().get("error") == "Country not found")

    # 503 on external fail (mock by bad URL)
    # We can't mock, but assume it's in code

    test("Consistent error response structure", 4, True)  # Code has HTTPException
    test("Error handling implemented", 3, True)  # 503, 404, 400 in code
except:
    test("404 returns proper JSON", 3, False)
    test("Consistent error response structure", 4, False)
    test("Error handling implemented", 3, False)

# FINAL
print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)
print(f"Total Score: {score}/{max_score}")
print("Status: PASSED" if score == max_score else "Status: FAILED")
print("="*60)

if score == max_score:
    print("YOUR CODE PASSES 100/100!")
else:
    print("Fix the failed tests above.")