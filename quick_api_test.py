import requests
import json
import uuid
import time

def test_vpc_creation():
    """Test VPC creation with proper header and unique stack name"""
    
    
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())
    stack_name = f"test-vpc-{timestamp}-{unique_id}"
    
    url = "http://3.111.234.240:8081/cloud/vpc"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-TenantID": "tata",
        "organization-name": "caltestorg"  
    }
    
    payload = {
        "cidrBlock": "10.11.0.0/16",
        "cloudAccountId": 1,
        "cloudProvider": "aws",
        "cloudRegion": "us-east-1",
        "name": stack_name,
        "stackName": stack_name,  
        "tags": {
            "Name": "qa-automation"
        }
    }
    
    print(f"=== Testing VPC Creation with Unique Stack Name ===")
    print(f"Stack Name: {stack_name}")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response Body: {json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response Body (raw): {response.text}")
        
        if response.status_code in [200, 201, 202]:  # Accept various success codes
            print(" SUCCESS: VPC creation initiated successfully")
            return True
        elif response.status_code == 409:
            print(" WARNING: Conflict detected - possibly duplicate stack name")
            return False
        else:
            print(f"FAILED: Unexpected status code {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"REQUEST FAILED: {e}")
        return False

def test_caltestorg_only():
    """Test with confirmed caltestorg organization"""
    
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())
    stack_name = f"test-vpc-caltestorg-{timestamp}-{unique_id}"
    
    url = "http://3.111.234.240:8081/cloud/vpc"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-TenantID": "tata",
        "organization-name": "caltestorg"  
    }
    
    payload = {
        "cidrBlock": "10.12.0.0/16",  
        "cloudAccountId": 1,
        "cloudProvider": "aws",
        "cloudRegion": "us-east-1",
        "name": stack_name,
        "stackName": stack_name,
        "tags": {
            "Name": "qa-automation-caltestorg"
        }
    }
    
    print(f"\n=== Testing with caltestorg Organization ===")
    print(f"Stack Name: {stack_name}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            print("SUCCESS: caltestorg organization works")
            return True
        else:
            try:
                error_msg = response.json()
                print(f"FAILED: {error_msg}")
            except:
                print(f"FAILED: Status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"REQUEST FAILED: {e}")
        return False

if __name__ == "__main__":
    print("Starting API Tests...")
    
    
    success1 = test_vpc_creation()
    
    
    success2 = test_caltestorg_only()
    
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"Test 1 (caltestorg): {'PASSED' if success1 else 'FAILED'}")
    print(f"Test 2 (caltestorg): {'PASSED' if success2 else 'FAILED'}")
    
    if success1 or success2:
        print(f"\nRECOMMENDATION: Use 'organization-name' as HEADER (not query param)")
        print("The API correctly requires this header for authentication.")
    else:
        print(f"\nBoth tests failed - check API endpoint and credentials")