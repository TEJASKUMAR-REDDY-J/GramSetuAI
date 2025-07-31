"""
Simple Platform Launcher
Launches both Borrower Platform (7861) and MFI Platform (7862) simultaneously
"""

import subprocess
import threading
import time
import os
import sys

def launch_borrower_platform():
    """Launch the borrower platform on port 7861"""
    try:
        print("🚀 Starting Borrower Platform on http://localhost:7861...")
        os.chdir(os.path.join(os.path.dirname(__file__), 'borrower_platform'))
        subprocess.run([sys.executable, 'borrower_app.py'], check=True)
    except Exception as e:
        print(f"❌ Error starting Borrower Platform: {e}")

def launch_mfi_platform():
    """Launch the MFI platform on port 7862"""
    try:
        print("🚀 Starting MFI Platform on http://localhost:7862...")
        os.chdir(os.path.join(os.path.dirname(__file__), 'microfinance_platform'))
        subprocess.run([sys.executable, 'mfi_app.py'], check=True)
    except Exception as e:
        print(f"❌ Error starting MFI Platform: {e}")

def main():
    """Launch both platforms simultaneously"""
    print("🏦 GramSetuAI - Complete Microfinance Platform")
    print("=" * 50)
    print("Starting both platforms...")
    print()
    
    # Start both platforms in separate threads
    borrower_thread = threading.Thread(target=launch_borrower_platform, daemon=True)
    mfi_thread = threading.Thread(target=launch_mfi_platform, daemon=True)
    
    # Start the threads
    borrower_thread.start()
    time.sleep(2)  # Small delay to avoid port conflicts
    mfi_thread.start()
    
    print()
    print("✅ Both platforms are starting...")
    print("📱 Borrower Platform: http://localhost:7861")
    print("🏢 MFI Platform: http://localhost:7862")
    print()
    print("Press Ctrl+C to stop both platforms")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down platforms...")
        print("👋 Thank you for using GramSetuAI!")

if __name__ == "__main__":
    main()
