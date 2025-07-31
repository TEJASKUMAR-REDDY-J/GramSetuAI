"""
Shared Loan Database Management
Handles loan applications, approvals, and EMI tracking between borrower and MFI platforms
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

class LoanDatabase:
    def __init__(self):
        # Use absolute path to ensure it works from any directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(base_dir, "shared_data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.applications_file = os.path.join(self.data_dir, "loan_applications.json")
        self.mfi_list_file = os.path.join(self.data_dir, "mfi_directory.json")
        self.emi_tracking_file = os.path.join(self.data_dir, "emi_tracking.json")
        
        # Initialize files
        self._initialize_files()
        
        # Load data
        self.applications = self._load_json(self.applications_file)
        self.mfi_directory = self._load_json(self.mfi_list_file)
        self.emi_tracking = self._load_json(self.emi_tracking_file)
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        if not os.path.exists(self.applications_file):
            with open(self.applications_file, 'w') as f:
                json.dump({"applications": {}, "approved_loans": {}}, f, indent=2)
        
        if not os.path.exists(self.mfi_list_file):
            with open(self.mfi_list_file, 'w') as f:
                json.dump({}, f, indent=2)
        
        if not os.path.exists(self.emi_tracking_file):
            with open(self.emi_tracking_file, 'w') as f:
                json.dump({}, f, indent=2)
    
    def _load_json(self, filepath: str) -> Dict:
        """Load JSON file safely"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, data: Dict, filepath: str):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving to {filepath}: {e}")
    
    def register_mfi(self, mfi_data: Dict) -> bool:
        """Register an MFI in the directory"""
        try:
            mfi_id = mfi_data.get('mfi_id')
            if not mfi_id:
                return False
            
            # Extract data from nested structure
            basic_details = mfi_data.get('basic_details', {})
            operational_metrics = mfi_data.get('operational_metrics', {})
            target_segments = mfi_data.get('target_segments', {})
            financial_compliance = mfi_data.get('financial_compliance', {})
            
            self.mfi_directory[mfi_id] = {
                'name': basic_details.get('mfi_name', 'Unknown MFI'),
                'location': f"{basic_details.get('head_office_address', '')}, {basic_details.get('operating_states', '')}".strip(', '),
                'contact': basic_details.get('contact_person', {}).get('name', ''),
                'phone': basic_details.get('contact_person', {}).get('phone', ''),
                'email': basic_details.get('contact_person', {}).get('email', ''),
                'interest_rates': financial_compliance.get('interest_rates', 'Not specified'),
                'loan_products': operational_metrics.get('loan_products', 'Standard loans').split(',') if operational_metrics.get('loan_products') else ['Standard loans'],
                'minimum_loan': int(operational_metrics.get('minimum_loan_amount', 5000)),
                'maximum_loan': int(operational_metrics.get('maximum_loan_amount', 100000)),
                'registration_date': datetime.now().isoformat(),
                'status': 'active'
            }
            
            self._save_json(self.mfi_directory, self.mfi_list_file)
            return True
        except Exception as e:
            print(f"Error registering MFI: {e}")
            return False
    
    def get_available_mfis(self) -> List[Dict]:
        """Get list of available MFIs for borrowers"""
        active_mfis = []
        for mfi_id, mfi_data in self.mfi_directory.items():
            if mfi_data.get('status') == 'active':
                active_mfis.append({
                    'mfi_id': mfi_id,
                    'name': mfi_data['name'],
                    'location': mfi_data['location'],
                    'min_loan': mfi_data['minimum_loan'],
                    'max_loan': mfi_data['maximum_loan'],
                    'products': mfi_data.get('loan_products', [])
                })
        return active_mfis
    
    def submit_loan_application(self, borrower_data: Dict, mfi_id: str, loan_details: Dict) -> str:
        """Submit a new loan application"""
        try:
            app_id = f"APP_{str(uuid.uuid4())[:8]}_{datetime.now().strftime('%Y%m%d')}"
            
            application = {
                'application_id': app_id,
                'borrower_id': borrower_data.get('phone_number', ''),
                'borrower_name': borrower_data.get('full_name', ''),
                'mfi_id': mfi_id,
                'loan_amount': loan_details.get('amount', 0),
                'loan_purpose': loan_details.get('purpose', ''),
                'loan_tenure': loan_details.get('tenure_months', 12),
                'application_date': datetime.now().isoformat(),
                'status': 'pending',
                'borrower_profile': borrower_data,
                'documents': loan_details.get('documents', []),
                'credit_score': borrower_data.get('credit_score', 0),
                'monthly_income': borrower_data.get('monthly_income', 0),
                'existing_loans': borrower_data.get('existing_loans', ''),
                'collateral': loan_details.get('collateral', ''),
                'guarantor': loan_details.get('guarantor', {})
            }
            
            if 'applications' not in self.applications:
                self.applications['applications'] = {}
            
            self.applications['applications'][app_id] = application
            self._save_json(self.applications, self.applications_file)
            
            return app_id
        except Exception as e:
            print(f"Error submitting application: {e}")
            return ""
    
    def get_applications_for_mfi(self, mfi_id: str) -> List[Dict]:
        """Get all applications for a specific MFI"""
        applications = []
        for app_id, app_data in self.applications.get('applications', {}).items():
            if app_data.get('mfi_id') == mfi_id:
                applications.append(app_data)
        return applications
    
    def get_applications_for_borrower(self, borrower_id: str) -> List[Dict]:
        """Get all applications for a specific borrower"""
        applications = []
        for app_id, app_data in self.applications.get('applications', {}).items():
            if app_data.get('borrower_id') == borrower_id:
                applications.append(app_data)
        return applications
    
    def approve_loan(self, app_id: str, approval_data: Dict) -> bool:
        """Approve a loan application"""
        try:
            if app_id not in self.applications.get('applications', {}):
                return False
            
            application = self.applications['applications'][app_id]
            application['status'] = 'approved'
            application['approval_date'] = datetime.now().isoformat()
            application['approved_amount'] = approval_data.get('approved_amount', application['loan_amount'])
            application['interest_rate'] = approval_data.get('interest_rate', 12.0)
            application['approval_comments'] = approval_data.get('comments', '')
            application['disbursement_date'] = approval_data.get('disbursement_date', '')
            
            # Move to approved loans
            if 'approved_loans' not in self.applications:
                self.applications['approved_loans'] = {}
            
            # Calculate EMI
            loan_amount = application['approved_amount']
            tenure_months = application['loan_tenure']
            monthly_rate = application['interest_rate'] / 100 / 12
            
            if monthly_rate > 0:
                emi = loan_amount * monthly_rate * (1 + monthly_rate)**tenure_months / ((1 + monthly_rate)**tenure_months - 1)
            else:
                emi = loan_amount / tenure_months
            
            application['emi_amount'] = round(emi, 2)
            application['total_amount'] = round(emi * tenure_months, 2)
            
            self.applications['approved_loans'][app_id] = application
            
            # Initialize EMI tracking
            self._initialize_emi_tracking(app_id, application)
            
            self._save_json(self.applications, self.applications_file)
            return True
        except Exception as e:
            print(f"Error approving loan: {e}")
            return False
    
    def reject_loan(self, app_id: str, reason: str) -> bool:
        """Reject a loan application"""
        try:
            if app_id not in self.applications.get('applications', {}):
                return False
            
            self.applications['applications'][app_id]['status'] = 'rejected'
            self.applications['applications'][app_id]['rejection_date'] = datetime.now().isoformat()
            self.applications['applications'][app_id]['rejection_reason'] = reason
            
            self._save_json(self.applications, self.applications_file)
            return True
        except Exception as e:
            print(f"Error rejecting loan: {e}")
            return False
    
    def _initialize_emi_tracking(self, app_id: str, loan_data: Dict):
        """Initialize EMI tracking for approved loan"""
        try:
            self.emi_tracking[app_id] = {
                'loan_id': app_id,
                'borrower_id': loan_data['borrower_id'],
                'mfi_id': loan_data['mfi_id'],
                'principal_amount': loan_data['approved_amount'],
                'emi_amount': loan_data['emi_amount'],
                'tenure_months': loan_data['loan_tenure'],
                'interest_rate': loan_data['interest_rate'],
                'disbursement_date': loan_data.get('disbursement_date', ''),
                'payments': [],
                'outstanding_balance': loan_data['approved_amount'],
                'next_due_date': self._calculate_next_due_date(loan_data.get('disbursement_date', '')),
                'status': 'active'
            }
            self._save_json(self.emi_tracking, self.emi_tracking_file)
        except Exception as e:
            print(f"Error initializing EMI tracking: {e}")
    
    def _calculate_next_due_date(self, disbursement_date: str) -> str:
        """Calculate next EMI due date"""
        try:
            if disbursement_date:
                disburse_date = datetime.fromisoformat(disbursement_date.replace('Z', '+00:00'))
                next_due = disburse_date + timedelta(days=30)  # Monthly EMI
                return next_due.isoformat()
            return ""
        except:
            return ""
    
    def pay_emi(self, loan_id: str, payment_date: str = None) -> Dict:
        """Process EMI payment"""
        try:
            if loan_id not in self.emi_tracking:
                return {"success": False, "message": "Loan not found"}
            
            loan = self.emi_tracking[loan_id]
            if loan['status'] != 'active':
                return {"success": False, "message": "Loan is not active"}
            
            payment_date = payment_date or datetime.now().isoformat()
            emi_amount = loan['emi_amount']
            
            # Calculate principal and interest components
            outstanding = loan['outstanding_balance']
            monthly_rate = loan['interest_rate'] / 100 / 12
            interest_component = outstanding * monthly_rate
            principal_component = emi_amount - interest_component
            
            # Record payment
            payment = {
                'payment_id': f"PAY_{str(uuid.uuid4())[:8]}",
                'payment_date': payment_date,
                'emi_amount': emi_amount,
                'principal_component': round(principal_component, 2),
                'interest_component': round(interest_component, 2),
                'outstanding_before': round(outstanding, 2),
                'outstanding_after': round(outstanding - principal_component, 2)
            }
            
            loan['payments'].append(payment)
            loan['outstanding_balance'] = round(outstanding - principal_component, 2)
            
            # Check if loan is fully paid
            if loan['outstanding_balance'] <= 0:
                loan['status'] = 'completed'
                loan['completion_date'] = payment_date
            else:
                # Calculate next due date
                last_payment = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
                next_due = last_payment + timedelta(days=30)
                loan['next_due_date'] = next_due.isoformat()
            
            self._save_json(self.emi_tracking, self.emi_tracking_file)
            
            return {
                "success": True,
                "message": "Payment recorded successfully",
                "payment_details": payment,
                "remaining_balance": loan['outstanding_balance'],
                "next_due_date": loan.get('next_due_date', ''),
                "status": loan['status']
            }
        except Exception as e:
            return {"success": False, "message": f"Error processing payment: {e}"}
    
    def get_loan_status(self, borrower_id: str) -> List[Dict]:
        """Get loan status for borrower"""
        loans = []
        for loan_id, loan_data in self.emi_tracking.items():
            if loan_data['borrower_id'] == borrower_id:
                loans.append({
                    'loan_id': loan_id,
                    'mfi_name': self.mfi_directory.get(loan_data['mfi_id'], {}).get('name', 'Unknown MFI'),
                    'principal_amount': loan_data['principal_amount'],
                    'emi_amount': loan_data['emi_amount'],
                    'outstanding_balance': loan_data['outstanding_balance'],
                    'next_due_date': loan_data.get('next_due_date', ''),
                    'status': loan_data['status'],
                    'payments_made': len(loan_data['payments'])
                })
        return loans

# Global instance
loan_db = LoanDatabase()
