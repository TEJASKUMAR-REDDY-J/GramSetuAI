#!/usr/bin/env python3
"""
Simple MFI Platform Test
"""

import sys
import os
import json

# Add paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🏦 MFI PLATFORM TEST")
print("=" * 30)

try:
    # Test 1: Import MFI platform
    print("1️⃣ Testing MFI platform import...")
    import microfinance_platform.mfi_app as mfi_app
    print("✅ MFI platform imported successfully!")
    
    # Test 2: Check if we can access loan applications
    print("\n2️⃣ Testing loan application access...")
    
    # Simulate MFI login (set a test MFI)
    test_mfi_id = "TEST_COMPLETE_MFI"  # From our data
    mfi_app.current_mfi_id = test_mfi_id
    mfi_app.current_mfi_profile = {
        "basic_details": {
            "mfi_name": "Complete Test Bank"
        }
    }
    
    print(f"   Set MFI context: {test_mfi_id}")
    
    # Test 3: Try to view pending applications
    print("\n3️⃣ Testing view_pending_applications...")
    try:
        pending_apps = mfi_app.view_pending_applications()
        print(f"   Result length: {len(pending_apps)}")
        
        if "APP_" in pending_apps:
            print("✅ Applications are visible in MFI platform!")
            
            # Count applications
            app_count = pending_apps.count("APP_")
            print(f"   Found {app_count} applications in the display")
            
            # Test 4: Try to get a specific application for approval
            print("\n4️⃣ Testing application processing...")
            
            # Extract first application ID
            import re
            app_ids = re.findall(r'APP_[a-f0-9_]+', pending_apps)
            if app_ids:
                test_app_id = app_ids[0]
                print(f"   Testing with application ID: {test_app_id}")
                
                # Test credit analysis
                try:
                    credit_analysis = mfi_app.get_credit_analysis(test_app_id)
                    if credit_analysis and len(credit_analysis) > 100:
                        print("✅ Credit analysis working!")
                    else:
                        print("⚠️ Credit analysis may have issues")
                except Exception as e:
                    print(f"⚠️ Credit analysis error: {e}")
                
                # Test approval (with test data)
                try:
                    approval_result = mfi_app.approve_loan_application(
                        app_id=test_app_id,
                        approved_amount=45000,
                        interest_rate=12.0,
                        comments="Test approval via automation",
                        disbursement_date="2025-08-01"
                    )
                    
                    if "✅" in approval_result:
                        print("✅ Loan approval working!")
                        print("🎉 COMPLETE WORKFLOW SUCCESSFUL!")
                        
                        # Test 5: Verify loan status changed
                        print("\n5️⃣ Verifying loan status update...")
                        updated_apps = mfi_app.view_pending_applications()
                        if test_app_id not in updated_apps or "approved" in updated_apps.lower():
                            print("✅ Loan status updated correctly!")
                        else:
                            print("⚠️ Loan status may not have updated")
                            
                    else:
                        print(f"⚠️ Approval failed: {approval_result[:200]}...")
                        
                except Exception as e:
                    print(f"⚠️ Approval error: {e}")
            else:
                print("⚠️ No application IDs found in display")
        else:
            print("❌ No applications visible in MFI platform")
            print("   This means the MFI platform cannot see loan applications")
            
    except Exception as e:
        print(f"❌ view_pending_applications error: {e}")
        import traceback
        traceback.print_exc()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   MFI platform still has import issues")
    
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n📊 SUMMARY")
print("=" * 30)
print("This test checks if:")
print("✓ MFI platform can be imported")
print("✓ MFI platform can see loan applications") 
print("✓ MFI platform can process applications")
print("✓ Complete borrower→MFI workflow works")
