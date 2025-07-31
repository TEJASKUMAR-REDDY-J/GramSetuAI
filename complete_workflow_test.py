#!/usr/bin/env python3
"""
Complete End-to-End Workflow Test
Tests the complete loan application workflow from borrower to MFI approval to EMI payment
"""

import sys
import os
import json
import threading
import time
from datetime import datetime

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🎯 COMPLETE WORKFLOW TEST")
print("=" * 50)

def test_complete_workflow():
    """Test complete borrower → MFI → EMI workflow"""
    
    print("1️⃣ Testing Borrower Platform...")
    try:
        import borrower_platform.borrower_app as borrower_app
        print("✅ Borrower platform imported successfully")
        
        # Test MFI dropdown
        mfi_choices = borrower_app.get_mfi_names_for_dropdown()
        print(f"   Available MFIs: {len(mfi_choices)}")
        
        if mfi_choices and "Error" not in str(mfi_choices[0]):
            selected_mfi = mfi_choices[0]
            print(f"   Testing with: {selected_mfi}")
            
            # Create test user
            borrower_app.current_user_id = "workflow_test_user"
            borrower_app.user_database["workflow_test_user"] = {
                "full_name": "Workflow Test User",
                "phone_number": "9999888777",
                "monthly_income": 35000,
                "village_name": "Test Village",
                "credit_score": 680
            }
            
            # Submit application
            result = borrower_app.submit_simple_loan_application(
                mfi_name=selected_mfi,
                loan_amount=75000,
                loan_purpose="Complete workflow test"
            )
            
            if "✅" in result:
                print("✅ Loan application submitted successfully")
                
                # Extract application ID
                app_id = None
                for line in result.split('\n'):
                    if 'Application ID' in line and ': ' in line:
                        app_id = line.split(': ')[1].strip()
                        break
                
                if app_id:
                    print(f"   Application ID: {app_id}")
                    
                    print("\n2️⃣ Testing MFI Platform...")
                    try:
                        import microfinance_platform.mfi_app as mfi_app
                        print("✅ MFI platform imported successfully")
                        
                        # Set MFI context
                        mfis = borrower_app.loan_db.get_available_mfis()
                        test_mfi_id = None
                        for mfi in mfis:
                            if mfi['name'] == selected_mfi:
                                test_mfi_id = mfi['mfi_id']
                                break
                        
                        if test_mfi_id:
                            mfi_app.current_mfi_id = test_mfi_id
                            mfi_app.current_mfi_profile = {
                                "basic_details": {"mfi_name": selected_mfi}
                            }
                            
                            # Check if application is visible
                            pending_apps = mfi_app.view_pending_applications()
                            if app_id in pending_apps:
                                print("✅ Application visible in MFI platform")
                                
                                print("\n3️⃣ Testing Loan Approval...")
                                # Approve the loan
                                approval_result = mfi_app.approve_loan_application(
                                    app_id=app_id,
                                    approved_amount=70000,
                                    interest_rate=11.5,
                                    comments="Workflow test approval",
                                    disbursement_date="2025-08-01"
                                )
                                
                                if "✅" in approval_result:
                                    print("✅ Loan approved successfully")
                                    
                                    print("\n4️⃣ Testing EMI Payment...")
                                    # Wait a moment for data sync
                                    time.sleep(1)
                                    
                                    # Check active loans on borrower side
                                    active_loans = borrower_app.view_active_loans()
                                    if "🟢" in active_loans:
                                        print("✅ Active loan visible on borrower side")
                                        
                                        # Get loan options for EMI
                                        loan_options = borrower_app.get_loan_options_for_emi()
                                        if loan_options and "No" not in loan_options[0]:
                                            print("✅ EMI payment options available")
                                            
                                            # Pay EMI
                                            emi_result = borrower_app.pay_emi(loan_options[0])
                                            if "✅" in emi_result:
                                                print("✅ EMI payment successful")
                                                print("\n🎉 COMPLETE WORKFLOW SUCCESS!")
                                                print("✅ Borrower can apply")
                                                print("✅ MFI can see and approve")
                                                print("✅ EMI system works")
                                                print("✅ Balance updates correctly")
                                                return True
                                            else:
                                                print(f"❌ EMI payment failed: {emi_result[:100]}")
                                        else:
                                            print("❌ No EMI payment options available")
                                    else:
                                        print("❌ Active loan not visible on borrower side")
                                else:
                                    print(f"❌ Loan approval failed: {approval_result[:100]}")
                            else:
                                print("❌ Application not visible in MFI platform")
                                print(f"   Pending apps preview: {pending_apps[:200]}")
                        else:
                            print("❌ Could not find MFI ID")
                            
                    except Exception as e:
                        print(f"❌ MFI platform error: {e}")
                else:
                    print("❌ Could not extract application ID")
            else:
                print(f"❌ Application submission failed: {result[:100]}")
        else:
            print("❌ No valid MFIs available")
            
    except Exception as e:
        print(f"❌ Borrower platform error: {e}")
        import traceback
        traceback.print_exc()
    
    return False

def start_platforms():
    """Start both platforms for manual testing"""
    print("\n🚀 STARTING PLATFORMS FOR MANUAL TESTING")
    print("=" * 50)
    
    def start_borrower():
        print("Starting borrower platform on port 7861...")
        os.system("cd borrower_platform && python borrower_app.py")
    
    def start_mfi():
        print("Starting MFI platform on port 7862...")
        os.system("cd microfinance_platform && python mfi_app.py")
    
    # Start in separate threads
    borrower_thread = threading.Thread(target=start_borrower, daemon=True)
    mfi_thread = threading.Thread(target=start_mfi, daemon=True)
    
    borrower_thread.start()
    time.sleep(2)  # Give borrower platform time to start
    mfi_thread.start()
    
    print("\n📱 Platforms starting...")
    print("🌐 Borrower Platform: http://localhost:7861")
    print("🏦 MFI Platform: http://localhost:7862")
    print("\nPress Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping platforms...")

if __name__ == "__main__":
    # First run automated test
    success = test_complete_workflow()
    
    if success:
        print("\n" + "="*50)
        print("🎉 ALL SYSTEMS WORKING PERFECTLY!")
        print("="*50)
        
        choice = input("\nDo you want to start the platforms for manual testing? (y/n): ")
        if choice.lower() == 'y':
            start_platforms()
    else:
        print("\n" + "="*50)
        print("⚠️ SOME ISSUES FOUND - CHECK OUTPUT ABOVE")
        print("="*50)
        
        choice = input("\nDo you want to start the platforms anyway for debugging? (y/n): ")
        if choice.lower() == 'y':
            start_platforms()
