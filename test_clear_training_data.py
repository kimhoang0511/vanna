"""
Test script for clear_training_data endpoint
Tests both locally and on Railway production
"""
import requests
import json

# Configuration
API_KEY = "L8WBBkJndxkbEJkMpCdOPmGc29HfWSTz"
RAILWAY_URL = "https://vanna-production.up.railway.app"
LOCAL_URL = "http://localhost:8000"

# Use Railway by default
BASE_URL = RAILWAY_URL

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_get_training_data():
    """Get current training data"""
    print_section("1. Get Current Training Data")
    
    response = requests.get(
        f"{BASE_URL}/training_data",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data.get("success"):
        count = data.get("data", {}).get("count", 0)
        print(f"\n✅ Found {count} training items")
        return count
    else:
        print(f"\n❌ Failed to get training data")
        return 0

def test_clear_training_data():
    """Clear all training data"""
    print_section("2. Clear All Training Data")
    
    response = requests.post(
        f"{BASE_URL}/clear_training_data",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data.get("success"):
        cleared = data.get("data", {}).get("cleared", 0)
        print(f"\n✅ Cleared {cleared} training items")
        return True
    else:
        print(f"\n❌ Failed to clear training data")
        return False

def test_verify_cleared():
    """Verify data is cleared"""
    print_section("3. Verify Data is Cleared")
    
    response = requests.get(
        f"{BASE_URL}/training_data",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data.get("success"):
        count = data.get("data", {}).get("count", 0)
        if count == 0:
            print(f"\n✅ Verified: All training data cleared (0 items)")
            return True
        else:
            print(f"\n⚠️  Warning: Still {count} items remaining")
            return False
    else:
        print(f"\n❌ Failed to verify")
        return False

def test_train_sample_data():
    """Train some sample data for testing"""
    print_section("4. Train Sample Data")
    
    # Train DDL
    print("Training DDL...")
    response = requests.post(
        f"{BASE_URL}/train/ddl",
        headers=headers,
        json={
            "ddl": "CREATE TABLE test_customers (id INT PRIMARY KEY, name VARCHAR(100));"
        }
    )
    print(f"DDL Status: {response.status_code}")
    print(f"DDL Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # Train Documentation
    print("\nTraining Documentation...")
    response = requests.post(
        f"{BASE_URL}/train/documentation",
        headers=headers,
        json={
            "documentation": "Bảng test_customers chứa thông tin khách hàng test."
        }
    )
    print(f"Docs Status: {response.status_code}")
    print(f"Docs Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # Train SQL
    print("\nTraining SQL...")
    response = requests.post(
        f"{BASE_URL}/train/sql",
        headers=headers,
        json={
            "question": "Lấy tất cả khách hàng",
            "sql": "SELECT * FROM test_customers;"
        }
    )
    print(f"SQL Status: {response.status_code}")
    print(f"SQL Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    print(f"\n✅ Sample data trained")

def test_final_verification():
    """Final verification"""
    print_section("5. Final Verification")
    
    response = requests.get(
        f"{BASE_URL}/training_data",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if data.get("success"):
        count = data.get("data", {}).get("count", 0)
        training_data = data.get("data", {}).get("data", [])
        
        print(f"\n✅ Found {count} training items:")
        for idx, item in enumerate(training_data, 1):
            item_type = item.get("training_data_type", "unknown")
            item_id = item.get("id", "no-id")
            print(f"  {idx}. Type: {item_type}, ID: {item_id}")
        
        return count == 3
    else:
        print(f"\n❌ Failed to verify")
        return False

def main():
    print_section("🧪 Test Clear Training Data Endpoint")
    print(f"Testing API: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    
    try:
        # Initialize Vanna first
        print_section("0. Initialize Vanna")
        response = requests.post(
            f"{BASE_URL}/init",
            headers=headers,
            json={"model": "gpt-4o-mini"}
        )
        print(f"Init Status: {response.status_code}")
        print(f"Init Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # Step 1: Get current training data
        count_before = test_get_training_data()
        
        # Step 2: Clear all training data
        if count_before > 0:
            test_clear_training_data()
        else:
            print("\n⚠️  No training data to clear, skipping clear step")
        
        # Step 3: Verify data is cleared
        test_verify_cleared()
        
        # Step 4: Train sample data
        test_train_sample_data()
        
        # Step 5: Final verification
        if test_final_verification():
            print_section("✅ All Tests Passed!")
            print("Clear training data endpoint is working correctly.")
            print("\nYou can now:")
            print("1. Use this endpoint in n8n workflow")
            print("2. Clear old data before retraining")
            print("3. Keep your RAG system up-to-date")
        else:
            print_section("⚠️  Tests Completed with Warnings")
            print("Please check the results above.")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Cannot connect to {BASE_URL}")
        print("Make sure the server is running.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
