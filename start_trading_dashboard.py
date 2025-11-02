#!/usr/bin/env python3
"""
Complete Trading Dashboard Startup Script
This script will start both backend and frontend servers and open the dashboard
"""

import subprocess
import time
import webbrowser
import requests
import os
import sys
from pathlib import Path

class TradingDashboardStarter:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = Path(__file__).parent
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check Python dependencies
        try:
            import fastapi, uvicorn, sqlalchemy, redis, pandas, numpy, tensorflow
            print("✅ Python dependencies: OK")
        except ImportError as e:
            print(f"❌ Missing Python dependency: {e}")
            print("💡 Run: pip install -r requirements.txt")
            return False
        
        # Check Node.js
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Node.js/npm: OK")
            else:
                print("❌ Node.js/npm not found")
                return False
        except FileNotFoundError:
            print("❌ Node.js/npm not found")
            print("💡 Install Node.js from: https://nodejs.org/")
            return False
        
        return True
    
    def setup_database(self):
        """Set up database with migrations"""
        print("💾 Setting up database...")
        
        try:
            # Run Alembic migrations
            result = subprocess.run(['alembic', 'upgrade', 'head'], 
                                  capture_output=True, text=True, cwd=self.base_dir)
            if result.returncode == 0:
                print("✅ Database migrations: OK")
                return True
            else:
                print(f"⚠️  Database migration warning: {result.stderr}")
                return True  # Continue anyway
        except FileNotFoundError:
            print("⚠️  Alembic not found, skipping migrations")
            return True
    
    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting backend server...")
        
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for backend to start
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get('http://localhost:8000/api/v1/health', timeout=1)
                    if response.status_code == 200:
                        print("✅ Backend server: Running on http://localhost:8000")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Backend server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def install_frontend_deps(self):
        """Install frontend dependencies if needed"""
        frontend_dir = self.base_dir / 'frontend'
        node_modules = frontend_dir / 'node_modules'
        
        if not node_modules.exists():
            print("📦 Installing frontend dependencies...")
            try:
                result = subprocess.run(['npm', 'install'], 
                                      cwd=frontend_dir, 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ Frontend dependencies: Installed")
                    return True
                else:
                    print(f"❌ Frontend install failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Frontend install error: {e}")
                return False
        else:
            print("✅ Frontend dependencies: Already installed")
            return True
    
    def start_frontend(self):
        """Start the React frontend server"""
        print("🎨 Starting frontend server...")
        
        frontend_dir = self.base_dir / 'frontend'
        
        try:
            self.frontend_process = subprocess.Popen(
                ['npm', 'start'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for frontend to start
            for i in range(60):  # Wait up to 60 seconds for React to compile
                try:
                    response = requests.get('http://localhost:3000', timeout=1)
                    if response.status_code == 200:
                        print("✅ Frontend server: Running on http://localhost:3000")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ Frontend server failed to start")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def create_test_user(self):
        """Create a test user account"""
        print("👤 Setting up test user...")
        
        try:
            user_data = {
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "testpassword123"
            }
            
            response = requests.post(
                "http://localhost:8000/api/v1/auth/register",
                json=user_data,
                timeout=5
            )
            
            if response.status_code in [201, 400]:  # 201 = created, 400 = already exists
                print("✅ Test user: Ready (testuser / testpassword123)")
                return True
            else:
                print(f"⚠️  Test user creation: {response.status_code}")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"⚠️  Test user setup: {e}")
            return True  # Continue anyway
    
    def open_dashboard(self):
        """Open the dashboard in the browser"""
        print("🌐 Opening trading dashboard...")
        
        try:
            webbrowser.open('http://localhost:3000')
            print("✅ Dashboard opened in browser")
            return True
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
            print("💡 Manually open: http://localhost:3000")
            return True
    
    def show_status(self):
        """Show system status and instructions"""
        print("\n" + "="*60)
        print("🎉 TRADING DASHBOARD - READY!")
        print("="*60)
        
        print("\n🌐 Access Points:")
        print("   • Trading Dashboard: http://localhost:3000")
        print("   • Backend API: http://localhost:8000")
        print("   • API Documentation: http://localhost:8000/docs")
        
        print("\n🔑 Login Credentials:")
        print("   • Username: testuser")
        print("   • Password: testpassword123")
        
        print("\n🎯 Features Available:")
        print("   ✅ Interactive Candlestick Charts")
        print("   ✅ AI/ML Price Predictions")
        print("   ✅ Trading Signal Generation")
        print("   ✅ Support/Resistance Levels")
        print("   ✅ Multi-timeframe Analysis")
        print("   ✅ Real-time Market Data")
        
        print("\n📊 How to Use:")
        print("   1. Login with the credentials above")
        print("   2. Click '📈 Trading' in the navigation")
        print("   3. Select symbols and timeframes")
        print("   4. View charts and trading signals")
        print("   5. Generate AI predictions")
        
        print("\n⚠️  To Stop Servers:")
        print("   Press Ctrl+C in this terminal")
        
    def cleanup(self):
        """Clean up processes"""
        print("\n🛑 Shutting down servers...")
        
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend server stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend server stopped")
    
    def start(self):
        """Start the complete trading dashboard system"""
        print("🚀 TRADING DASHBOARD STARTUP")
        print("="*60)
        
        try:
            # Step 1: Check dependencies
            if not self.check_dependencies():
                return False
            
            # Step 2: Setup database
            if not self.setup_database():
                return False
            
            # Step 3: Start backend
            if not self.start_backend():
                return False
            
            # Step 4: Install frontend dependencies
            if not self.install_frontend_deps():
                return False
            
            # Step 5: Start frontend
            if not self.start_frontend():
                return False
            
            # Step 6: Create test user
            self.create_test_user()
            
            # Step 7: Open dashboard
            self.open_dashboard()
            
            # Step 8: Show status
            self.show_status()
            
            # Keep running
            print("\n🔄 Servers running... Press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return True
            
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    """Main function"""
    starter = TradingDashboardStarter()
    starter.start()

if __name__ == "__main__":
    main()