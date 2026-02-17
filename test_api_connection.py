"""
API Connection Test Script
Tests all critical API endpoints to verify connectivity and functionality
"""
import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "v1"

def print_test(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")
    print()

def test_root_endpoint():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        passed = response.status_code == 200
        data = response.json() if passed else {}
        print_test(
            "Root Endpoint",
            passed,
            f"Status: {response.status_code}, Message: {data.get('message', 'N/A')}"
        )
        return passed
    except Exception as e:
        print_test("Root Endpoint", False, f"Error: {str(e)}")
        return False

def test_health_endpoint():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        passed = response.status_code == 200
        data = response.json() if passed else {}
        print_test(
            "Health Check",
            passed,
            f"Status: {data.get('status', 'N/A')}, Checks: {data.get('checks', {})}"
        )
        return passed
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False

def test_api_docs():
    """Test API documentation endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        passed = response.status_code == 200
        print_test(
            "API Documentation",
            passed,
            f"Status: {response.status_code}"
        )
        return passed
    except Exception as e:
        print_test("API Documentation", False, f"Error: {str(e)}")
        return False

def test_register_user():
    """Test user registration"""
    try:
        test_user = {
            "username": f"testuser_{datetime.now().timestamp()}",
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "TestPassword123!"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/{API_VERSION}/auth/register",
            json=test_user,
            timeout=5
        )
        
        passed = response.status_code in [200, 201, 400]  # 400 if user exists
        data = response.json() if response.status_code in [200, 201] else {}
        
        print_test(
            "User Registration",
            passed,
            f"Status: {response.status_code}, User: {data.get('username', 'N/A')}"
        )
        return passed, test_user
    except Exception as e:
        print_test("User Registration", False, f"Error: {str(e)}")
        return False, None

def test_login(username, password):
    """Test user login"""
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/api/{API_VERSION}/auth/login",
            json=login_data,
            timeout=5
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        token = data.get('access_token', '')
        
        print_test(
            "User Login",
            passed,
            f"Status: {response.status_code}, Token: {'Present' if token else 'Missing'}"
        )
        return passed, token
    except Exception as e:
        print_test("User Login", False, f"Error: {str(e)}")
        return False, None

def test_protected_endpoint(token):
    """Test protected endpoint with authentication"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/{API_VERSION}/auth/me",
            headers=headers,
            timeout=5
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test(
            "Protected Endpoint (Get User)",
            passed,
            f"Status: {response.status_code}, User: {data.get('username', 'N/A')}"
        )
        return passed
    except Exception as e:
        print_test("Protected Endpoint", False, f"Error: {str(e)}")
        return False

def test_market_data_endpoint(token):
    """Test market data endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/{API_VERSION}/market-data/live/RELIANCE?timeframe=1D",
            headers=headers,
            timeout=10
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test(
            "Market Data Endpoint",
            passed,
            f"Status: {response.status_code}, Symbol: {data.get('symbol', 'N/A')}"
        )
        return passed
    except Exception as e:
        print_test("Market Data Endpoint", False, f"Error: {str(e)}")
        return False

def test_historical_data_endpoint(token):
    """Test historical data endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        payload = {
            "symbol": "RELIANCE",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "timeframe": "1D"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/{API_VERSION}/market-data/historical",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        print_test(
            "Historical Data Endpoint",
            passed,
            f"Status: {response.status_code}, Records: {data.get('count', 0)}"
        )
        return passed
    except Exception as e:
        print_test("Historical Data Endpoint", False, f"Error: {str(e)}")
        return False

def test_prediction_endpoint(token):
    """Test ML prediction endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "symbol": "RELIANCE",
            "timeframe": "1D",
            "time_horizon": "short"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/{API_VERSION}/predictions/generate",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        passed = response.status_code in [200, 400]  # 400 if insufficient data
        data = response.json() if response.status_code == 200 else {}
        
        print_test(
            "ML Prediction Endpoint",
            passed,
            f"Status: {response.status_code}, Prediction: {data.get('prediction', {}).get('predicted_price', 'N/A')}"
        )
        return passed
    except Exception as e:
        print_test("ML Prediction Endpoint", False, f"Error: {str(e)}")
        return False

def test_signal_endpoint(token):
    """Test trading signal endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "symbol": "RELIANCE",
            "timeframe": "1D"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/{API_VERSION}/signals/generate",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        passed = response.status_code in [200, 400]  # 400 if insufficient data
        data = response.json() if response.status_code == 200 else {}
        
        print_test(
            "Trading Signal Endpoint",
            passed,
            f"Status: {response.status_code}, Signal: {data.get('signal', {}).get('signal_type', 'N/A')}"
        )
        return passed
    except Exception as e:
        print_test("Trading Signal Endpoint", False, f"Error: {str(e)}")
        return False

def test_cors_headers():
    """Test CORS headers"""
    try:
        response = requests.options(f"{BASE_URL}/api/{API_VERSION}/auth/login", timeout=5)
        headers = response.headers
        
        has_cors = 'access-control-allow-origin' in [h.lower() for h in headers.keys()]
        
        print_test(
            "CORS Configuration",
            has_cors,
            f"CORS Headers: {'Present' if has_cors else 'Missing'}"
        )
        return has_cors
    except Exception as e:
        print_test("CORS Configuration", False, f"Error: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("=" * 60)
    print("API CONNECTION TEST SUITE")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"API Version: {API_VERSION}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    results = []
    
    # Test basic endpoints
    print("📡 Testing Basic Endpoints...")
    print("-" * 60)
    results.append(test_root_endpoint())
    results.append(test_health_endpoint())
    results.append(test_api_docs())
    results.append(test_cors_headers())
    
    # Test authentication
    print("\n🔐 Testing Authentication...")
    print("-" * 60)
    
    # Try with existing test user first
    login_success, token = test_login("testuser", "testpassword123")
    
    if not login_success:
        # Register new user if login fails
        reg_success, test_user = test_register_user()
        results.append(reg_success)
        
        if reg_success and test_user:
            login_success, token = test_login(test_user['username'], test_user['password'])
    
    results.append(login_success)
    
    # Test protected endpoints if we have a token
    if token:
        print("\n🔒 Testing Protected Endpoints...")
        print("-" * 60)
        results.append(test_protected_endpoint(token))
        
        print("\n📊 Testing Market Data Endpoints...")
        print("-" * 60)
        results.append(test_market_data_endpoint(token))
        results.append(test_historical_data_endpoint(token))
        
        print("\n🤖 Testing ML/AI Endpoints...")
        print("-" * 60)
        results.append(test_prediction_endpoint(token))
        results.append(test_signal_endpoint(token))
    else:
        print("\n⚠️  Skipping protected endpoint tests (no auth token)")
        results.extend([False, False, False, False, False])
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {percentage:.1f}%")
    print("=" * 60)
    
    if percentage >= 80:
        print("\n✅ API is working properly!")
        return 0
    elif percentage >= 50:
        print("\n⚠️  API is partially working - some issues detected")
        return 1
    else:
        print("\n❌ API has critical issues - please check the server")
        return 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        sys.exit(2)
