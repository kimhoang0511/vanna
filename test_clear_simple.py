"""
Quick test to verify clear_training_data actually removes data
"""
import requests
import json

API_KEY = "YOUR_API_KEY_HERE"
BASE_URL = "https://vanna-production.up.railway.app"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 70)
print("Testing Clear Training Data with Existing Data")
print("=" * 70)

# Step 1: Check current data
print("\n1. Current training data:")
response = requests.get(f"{BASE_URL}/training_data", headers=headers)
data = response.json()
count_before = data["data"]["count"]
print(f"   Count: {count_before}")

# Step 2: Clear data
print("\n2. Clearing training data...")
response = requests.post(f"{BASE_URL}/clear_training_data", headers=headers)
result = response.json()
print(f"   Response: {json.dumps(result, indent=2, ensure_ascii=False)}")

# Step 3: Verify cleared
print("\n3. Verify cleared:")
response = requests.get(f"{BASE_URL}/training_data", headers=headers)
data = response.json()
count_after = data["data"]["count"]
print(f"   Count: {count_after}")

# Step 4: Summary
print("\n" + "=" * 70)
if count_after == 0:
    print(f"✅ SUCCESS: Cleared {count_before} items, now {count_after} items")
else:
    print(f"⚠️  WARNING: Cleared {count_before - count_after} items, but {count_after} remain")
print("=" * 70)
