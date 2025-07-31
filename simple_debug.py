#!/usr/bin/env python3
"""
Simple debug test for loan application visibility
"""

import sys
import os
import json

# Add path
sys.path.append('.')

def simple_debug():
    print("🔍 Simple Debug Test")
    print("=" * 30)
    
    try:
        # Import modules
        from shared_data.loan_database import loan_db
        
        print("✅ Successfully imported loan_db")
        
        # Check applications
        all_apps = loan_db.applications.get('applications', {})
        print(f"📊 Total applications: {len(all_apps)}")
        
        # Show first few applications
        for i, (app_id, app_data) in enumerate(list(all_apps.items())[:3]):
            print(f"   {i+1}. {app_id}")
            print(f"      Borrower: {app_data.get('borrower_name', 'Unknown')}")
            print(f"      MFI ID: {app_data.get('mfi_id', 'Unknown')}")
            print(f"      Status: {app_data.get('status', 'Unknown')}")
            print(f"      Amount: ₹{app_data.get('loan_amount', 0):,}")
            print()
        
        # Check MFI directory
        print("🏦 MFI Directory:")
        for mfi_id, mfi_data in list(loan_db.mfi_directory.items())[:5]:
            print(f"   {mfi_id}: {mfi_data.get('name', 'Unknown')}")
        
        # Test specific MFI query
        if all_apps:
            first_app = next(iter(all_apps.values()))
            test_mfi_id = first_app.get('mfi_id')
            print(f"\n🔍 Testing query for MFI: {test_mfi_id}")
            
            apps_for_mfi = loan_db.get_applications_for_mfi(test_mfi_id)
            print(f"📄 Applications found: {len(apps_for_mfi)}")
            
            for app in apps_for_mfi:
                print(f"   - {app['application_id']}: {app['borrower_name']} (₹{app['loan_amount']:,})")
        
        # Test view_pending_applications function
        print(f"\n🔧 Testing MFI view function...")
        try:
            from microfinance_platform.mfi_app import view_pending_applications
            import microfinance_platform.mfi_app as mfi_app
            
            # Set a test MFI as logged in
            if loan_db.mfi_directory:
                test_mfi_id = list(loan_db.mfi_directory.keys())[0]
                mfi_app.current_mfi_id = test_mfi_id
                mfi_app.current_mfi_profile = {"basic_details": {"mfi_name": "Test MFI"}}
                
                print(f"   Set current MFI: {test_mfi_id}")
                
                result = view_pending_applications()
                print(f"   Result length: {len(result)}")
                print(f"   First 200 chars: {result[:200]}")
                
                if "No pending applications" in result:
                    print("   ⚠️ Function returns 'No pending applications'")
                    
                    # Debug further
                    print("   🔍 Debugging why no applications found...")
                    direct_apps = loan_db.get_applications_for_mfi(test_mfi_id)
                    print(f"   Direct query returns: {len(direct_apps)} applications")
                    
                    if direct_apps:
                        print("   ❌ Applications exist but not showing in view function!")
                        print(f"   First app MFI ID: {direct_apps[0]['mfi_id']}")
                        print(f"   Current MFI ID: {test_mfi_id}")
                        print(f"   Match: {direct_apps[0]['mfi_id'] == test_mfi_id}")
                else:
                    print("   ✅ Applications found in view function!")
            
        except Exception as e:
            print(f"   ❌ Error testing MFI view: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    simple_debug()
