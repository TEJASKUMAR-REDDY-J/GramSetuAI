#!/usr/bin/env python3
"""
Start Both Platforms - Simple launcher script with authentication fix info
"""

import os
import sys
import subprocess
import time

def start_platforms():
    """Start both borrower and MFI platforms"""
    print("🚀 Starting GramSetuAI Platforms - Authentication Fixed!")
    print("=" * 55)
    
    print("🔧 IMPORTANT CHANGES:")
    print("✅ MFI Platform: No more username/password needed!")
    print("✅ Simply select your MFI from dropdown to login")
    print("✅ All registered MFIs appear in the selection list")
    print("=" * 55)
    
    # Start borrower platform
    print("📱 Starting Borrower Platform...")
    borrower_cmd = [sys.executable, "borrower_platform/borrower_app.py"]
    borrower_process = subprocess.Popen(borrower_cmd, cwd=".")
    
    # Wait a moment
    time.sleep(3)
    
    # Start MFI platform  
    print("🏦 Starting MFI Platform...")
    mfi_cmd = [sys.executable, "microfinance_platform/mfi_app.py"]
    mfi_process = subprocess.Popen(mfi_cmd, cwd=".")
    
    print("\n✅ Both platforms starting...")
    print("🌐 Borrower Platform: http://localhost:7861")
    print("🏦 MFI Platform: http://localhost:7862")
    print("\n📋 How to test the FIXED authentication:")
    print("1. Open MFI platform: http://localhost:7862")
    print("2. Go to 'Authentication' tab")
    print("3. Select your MFI from the dropdown (no password needed!)")
    print("4. Click 'Login to Dashboard'")
    print("5. Access all loan applications and analytics")
    print("\n📝 Borrower → MFI workflow:")
    print("1. Open borrower platform: http://localhost:7861")
    print("2. Create user and submit loan application")
    print("3. Go to MFI platform and login")
    print("4. See application in 'Loan Management' tab")
    print("5. Approve loan and test EMI payments")
    print("\nPress Ctrl+C to stop both platforms")
    
    try:
        # Wait for processes
        borrower_process.wait()
        mfi_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping platforms...")
        borrower_process.terminate()
        mfi_process.terminate()
        print("👋 Platforms stopped")

if __name__ == "__main__":
    start_platforms()
