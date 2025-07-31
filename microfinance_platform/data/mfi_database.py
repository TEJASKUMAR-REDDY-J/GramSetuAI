"""
MFI Database Management
Handles microfinance institution data storage and retrieval
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib

class MFIDatabase:
    def __init__(self, data_dir: str = "microfinance_platform/data"):
        self.data_dir = data_dir
        self.mfi_data_file = os.path.join(data_dir, "mfi_profiles.json")
        self.login_data_file = os.path.join(data_dir, "mfi_logins.json")
        self.borrower_data_file = os.path.join(data_dir, "borrower_profiles.json")
        
        # Initialize data files if they don't exist
        self._initialize_data_files()
        
        # Load data into memory
        self.mfi_profiles = self._load_json_file(self.mfi_data_file)
        self.login_credentials = self._load_json_file(self.login_data_file)
        self.borrower_profiles = self._load_json_file(self.borrower_data_file)
        
    def _initialize_data_files(self):
        """Initialize data files with empty structures"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        if not os.path.exists(self.mfi_data_file):
            with open(self.mfi_data_file, 'w') as f:
                json.dump({}, f)
                
        if not os.path.exists(self.login_data_file):
            with open(self.login_data_file, 'w') as f:
                json.dump({}, f)
                
        if not os.path.exists(self.borrower_data_file):
            with open(self.borrower_data_file, 'w') as f:
                json.dump({}, f)
    
    def _load_json_file(self, filepath: str) -> Dict:
        """Load JSON file safely"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json_file(self, filepath: str, data: Dict):
        """Save data to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _hash_password(self, password: str) -> str:
        """Hash password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_mfi(self, mfi_data: Dict[str, Any], username: str, password: str) -> Dict[str, Any]:
        """
        Register a new MFI with login credentials
        
        Args:
            mfi_data: Complete MFI profile data
            username: Login username
            password: Login password
            
        Returns:
            Dict with registration result
        """
        try:
            # Generate unique MFI ID
            mfi_id = f"MFI_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Check if username already exists
            if username in self.login_credentials:
                return {"success": False, "error": "Username already exists"}
            
            # Add metadata to MFI data
            mfi_data["mfi_id"] = mfi_id
            mfi_data["registration_date"] = datetime.now().isoformat()
            mfi_data["last_updated"] = datetime.now().isoformat()
            mfi_data["status"] = "active"
            
            # Store MFI profile
            self.mfi_profiles[mfi_id] = mfi_data
            
            # Store login credentials
            self.login_credentials[username] = {
                "mfi_id": mfi_id,
                "password_hash": self._hash_password(password),
                "created_date": datetime.now().isoformat(),
                "last_login": None
            }
            
            # Save to files
            self._save_json_file(self.mfi_data_file, self.mfi_profiles)
            self._save_json_file(self.login_data_file, self.login_credentials)
            
            # Register in shared loan database for borrower visibility
            try:
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
                from shared_data.loan_database import loan_db
                
                # Add mfi_id to the data before registering
                mfi_data_with_id = mfi_data.copy()
                mfi_data_with_id['mfi_id'] = mfi_id
                
                success = loan_db.register_mfi(mfi_data_with_id)
                if success:
                    print(f"✅ MFI {mfi_id} registered in shared database")
                else:
                    print(f"❌ Failed to register MFI {mfi_id} in shared database")
            except Exception as e:
                print(f"Warning: Could not register MFI in shared database: {e}")
                import traceback
                traceback.print_exc()
            
            return {
                "success": True,
                "mfi_id": mfi_id,
                "message": "MFI registered successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def authenticate_mfi(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate MFI login
        
        Args:
            username: Login username
            password: Login password
            
        Returns:
            Dict with authentication result
        """
        try:
            if username not in self.login_credentials:
                return {"success": False, "error": "Invalid username"}
            
            user_data = self.login_credentials[username]
            password_hash = self._hash_password(password)
            
            if user_data["password_hash"] != password_hash:
                return {"success": False, "error": "Invalid password"}
            
            # Update last login
            user_data["last_login"] = datetime.now().isoformat()
            self.login_credentials[username] = user_data
            self._save_json_file(self.login_data_file, self.login_credentials)
            
            mfi_id = user_data["mfi_id"]
            mfi_profile = self.mfi_profiles.get(mfi_id, {})
            
            return {
                "success": True,
                "mfi_id": mfi_id,
                "mfi_profile": mfi_profile,
                "message": "Login successful"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_mfi_profile(self, mfi_id: str) -> Optional[Dict[str, Any]]:
        """Get MFI profile by ID"""
        return self.mfi_profiles.get(mfi_id)
    
    def update_mfi_profile(self, mfi_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update MFI profile"""
        try:
            if mfi_id not in self.mfi_profiles:
                return {"success": False, "error": "MFI not found"}
            
            # Preserve important fields
            updated_data["mfi_id"] = mfi_id
            updated_data["last_updated"] = datetime.now().isoformat()
            if "registration_date" not in updated_data:
                updated_data["registration_date"] = self.mfi_profiles[mfi_id].get("registration_date")
            
            self.mfi_profiles[mfi_id] = updated_data
            self._save_json_file(self.mfi_data_file, self.mfi_profiles)
            
            return {"success": True, "message": "Profile updated successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_borrower_data(self, borrower_id: str = None) -> Dict[str, Any]:
        """
        Get borrower data - interfaces with borrower platform
        This allows MFI agents to access borrower profiles for analysis
        """
        try:
            # Try to load from borrower platform
            borrower_file = "borrower_platform/user_data.json"
            if os.path.exists(borrower_file):
                with open(borrower_file, 'r') as f:
                    borrower_data = json.load(f)
                    
                if borrower_id:
                    return borrower_data.get(borrower_id, {})
                return borrower_data
            
            # Fallback to local borrower data
            if borrower_id:
                return self.borrower_profiles.get(borrower_id, {})
            return self.borrower_profiles
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_all_mfis(self) -> Dict[str, Any]:
        """Get all MFI profiles (for admin purposes)"""
        return self.mfi_profiles
    
    def search_mfis(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search MFIs based on filters"""
        results = []
        
        for mfi_id, mfi_data in self.mfi_profiles.items():
            match = True
            
            for key, value in filters.items():
                if key in mfi_data:
                    if isinstance(value, str) and value.lower() not in str(mfi_data[key]).lower():
                        match = False
                        break
                    elif isinstance(value, (int, float)) and mfi_data[key] != value:
                        match = False
                        break
            
            if match:
                results.append(mfi_data)
        
        return results

# Global instance
mfi_db = MFIDatabase()
