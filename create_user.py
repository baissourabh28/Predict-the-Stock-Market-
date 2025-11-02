"""
Script to create a test user account
"""
import requests
import json

def create_test_user():
    """Create a test user account"""
    
    # User registration data
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Register the user
        print("🔐 Creating test user account...")
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            user_info = response.json()
            print("✅ User created successfully!")
            print(f"   Username: {user_info['username']}")
            print(f"   Email: {user_info['email']}")
            print(f"   User ID: {user_info['id']}")
            
            # Now try to login
            print("\n🔑 Testing login...")
            login_data = {
                "username": user_data["username"],
                "password": user_data["password"]
            }
            
            login_response = requests.post(
                "http://localhost:8000/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                print("✅ Login successful!")
                print(f"   Access Token: {token_data['access_token'][:50]}...")
                print(f"   Token Type: {token_data['token_type']}")
                
                print("\n🎉 Account ready to use!")
                print(f"   Username: {user_data['username']}")
                print(f"   Password: {user_data['password']}")
                
                return True
            else:
                print(f"❌ Login failed: {login_response.json()}")
                return False
                
        elif response.status_code == 400:
            error_detail = response.json().get('detail', 'Unknown error')
            if 'already registered' in error_detail:
                print("ℹ️  User already exists, trying to login...")
                
                # Try to login with existing user
                login_data = {
                    "username": user_data["username"],
                    "password": user_data["password"]
                }
                
                login_response = requests.post(
                    "http://localhost:8000/api/v1/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if login_response.status_code == 200:
                    print("✅ Login with existing user successful!")
                    print(f"   Username: {user_data['username']}")
                    print(f"   Password: {user_data['password']}")
                    return True
                else:
                    print(f"❌ Login failed: {login_response.json()}")
                    return False
            else:
                print(f"❌ Registration failed: {error_detail}")
                return False
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Trading Dashboard - User Account Creation")
    print("=" * 50)
    
    if create_test_user():
        print("\n" + "=" * 50)
        print("🎯 READY TO USE!")
        print("=" * 50)
        print("You can now:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Login with:")
        print("   • Username: testuser")
        print("   • Password: testpassword123")
        print("3. Access the trading dashboard")
        print("4. Test market data and predictions")
    else:
        print("\n❌ Failed to create user account")
        print("Please check if the backend server is running on port 8000")

if __name__ == "__main__":
    main()