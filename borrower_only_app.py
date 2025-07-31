#!/usr/bin/env python3
"""
GramSetuAI Borrower Platform - Clean Focused UI
Comprehensive microfinance platform focused on borrower experience
"""

import gradio as gr
import json
import os
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
import pickle
import joblib

# File paths
BORROWER_DATA_FILE = "borrower_platform/user_data.json"

class BorrowerPlatform:
    def __init__(self):
        """Initialize the borrower platform with fixed credit scoring"""
        self.setup_data_storage()
        self.current_user = None
        
        # Load ML model for credit scoring
        self.load_credit_model()
        
        print("✅ Borrower Platform initialized successfully!")
    
    def setup_data_storage(self):
        """Setup data storage"""
        os.makedirs(os.path.dirname(BORROWER_DATA_FILE), exist_ok=True)
        
        if not os.path.exists(BORROWER_DATA_FILE):
            with open(BORROWER_DATA_FILE, 'w') as f:
                json.dump({}, f)
    
    def load_credit_model(self):
        """Load the ML model for credit scoring"""
        try:
            # Try to load the model
            with open('student_pipeline_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            print("✅ Credit scoring model loaded successfully")
        except:
            try:
                self.model = joblib.load('student_pipeline_model.pkl')
                print("✅ Credit scoring model loaded with joblib")
            except:
                print("⚠️ Credit model not found, using rule-based scoring")
                self.model = None
    
    def hash_password(self, password: str) -> str:
        """Hash password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_user_id(self, name: str, phone: str) -> str:
        """Generate unique user ID"""
        return f"{name}_{phone}"
    
    def load_borrower_data(self) -> Dict:
        """Load borrower data from file"""
        try:
            with open(BORROWER_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_borrower_data(self, data: Dict):
        """Save borrower data to file"""
        with open(BORROWER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_credit_score(self, user_data: Dict) -> float:
        """Calculate credit score using improved logic (300-900 scale)"""
        try:
            score = 300  # Base score
            
            # Age factor (0-50 points)
            age = user_data.get('age', 25)
            if 25 <= age <= 55:
                score += 50
            elif 21 <= age < 25 or 55 < age <= 65:
                score += 35
            else:
                score += 20
            
            # Income factor (0-100 points)
            income = user_data.get('monthly_income', 0)
            if income >= 100000:
                score += 100
            elif income >= 50000:
                score += 80
            elif income >= 30000:
                score += 60
            elif income >= 20000:
                score += 40
            else:
                score += 20
            
            # Employment type (0-50 points)
            occupation = user_data.get('primary_occupation', '').lower()
            if 'engineer' in occupation or 'doctor' in occupation or 'teacher' in occupation:
                score += 50
            elif 'business' in occupation or 'self' in occupation:
                score += 40
            elif 'farmer' in occupation:
                score += 35
            else:
                score += 25
            
            # Banking relationship (0-50 points)
            bank_account = user_data.get('bank_account_status', '').lower()
            if 'have' in bank_account:
                score += 50
            else:
                score += 10
            
            # Savings behavior (0-50 points)
            savings = user_data.get('savings_per_month', 0)
            income = user_data.get('monthly_income', 1)
            savings_ratio = savings / max(income, 1) if income > 0 else 0
            if savings_ratio >= 0.2:  # 20% savings
                score += 50
            elif savings_ratio >= 0.15:
                score += 40
            elif savings_ratio >= 0.1:
                score += 30
            else:
                score += 15
            
            # Digital literacy (0-40 points)
            digital_trans = user_data.get('digital_transaction_history', '').lower()
            if 'excellent' in digital_trans:
                score += 40
            elif 'good' in digital_trans:
                score += 30
            elif 'average' in digital_trans:
                score += 20
            else:
                score += 10
            
            # Utility payments (0-30 points)
            utility_payments = user_data.get('utility_bill_payments', '').lower()
            if 'on time' in utility_payments:
                score += 30
            elif 'mostly' in utility_payments:
                score += 25
            else:
                score += 10
            
            # Asset ownership (0-50 points)
            land_ownership = user_data.get('owns_land', '').lower()
            gold_grams = user_data.get('gold_grams', 0)
            
            asset_points = 0
            if 'both' in land_ownership or 'yes' in land_ownership:
                asset_points += 25
            if gold_grams > 50:
                asset_points += 25
            elif gold_grams > 20:
                asset_points += 15
            elif gold_grams > 0:
                asset_points += 10
            
            score += min(asset_points, 50)
            
            # Existing loans (penalty/bonus)
            existing_loans = user_data.get('existing_loans', '').lower()
            repayment_history = user_data.get('repayment_history', '').lower()
            
            if 'none' in existing_loans:
                score += 20  # No existing debt is good for new borrowers
            elif 'good' in repayment_history or 'excellent' in repayment_history:
                score += 30  # Good repayment history
            elif 'poor' in repayment_history:
                score -= 50  # Poor repayment is bad
            
            # Location factor (urban areas might have different risk)
            state = user_data.get('state', '').lower()
            if 'karnataka' in state or 'maharashtra' in state or 'tamil' in state:
                score += 20  # Developed states
            
            # Cap the score at 900
            final_score = min(score, 900)
            
            # Ensure minimum score of 300
            final_score = max(final_score, 300)
            
            return final_score
            
        except Exception as e:
            print(f"Credit scoring error: {e}")
            return 650  # Default reasonable score
    
    def get_risk_category(self, credit_score: float) -> Tuple[str, str]:
        """Get risk category and approval recommendation based on credit score"""
        if credit_score >= 750:
            return "Low Risk", "APPROVED - Excellent credit profile"
        elif credit_score >= 700:
            return "Low-Medium Risk", "APPROVED - Good credit profile"
        elif credit_score >= 650:
            return "Medium Risk", "REVIEW REQUIRED - Acceptable profile with conditions"
        elif credit_score >= 600:
            return "Medium-High Risk", "CONDITIONAL APPROVAL - Higher interest rates"
        else:
            return "High Risk", "REVIEW REQUIRED - Additional documentation needed"
    
    def register_borrower(self, full_name: str, phone_number: str, email: str, password: str, 
                         age: int, gender: str, preferred_language: str, aadhaar_number: str,
                         voter_id: str, marital_status: str, number_of_dependents: int,
                         village_name: str, district: str, state: str, pincode: str,
                         house_type: str, electricity_connection: str, primary_occupation: str,
                         secondary_income_sources: str, employment_type: str, seasonal_variation: str,
                         monthly_income: int, monthly_expenses: int, savings_per_month: int,
                         bank_account_status: str, bank_name: str, existing_loans: str,
                         repayment_history: str, group_membership: str, past_loan_amounts: str,
                         owns_smartphone: str, knows_how_to_use_apps: str, preferred_mode_of_communication: str,
                         internet_availability: str, digital_transaction_history: str,
                         utility_bill_payments: str, government_scheme_eligibility: str,
                         owns_land: str, land_area_text: str, land_type: str, patta_or_katha_number: str,
                         property_location: str, land_area: float, gold_grams: float,
                         livestock_ownership: str, vehicle_ownership: str, user_notes: str,
                         agent_observations: str) -> Tuple[str, bool]:
        """Register a new borrower with comprehensive profile data"""
        try:
            # Validate required fields
            required_fields = [full_name, phone_number, email, password, age, village_name, district, state, pincode, primary_occupation, monthly_income]
            if not all(required_fields):
                return "❌ Please fill all required fields", False
            
            user_id = self.generate_user_id(full_name, phone_number)
            borrower_data = self.load_borrower_data()
            
            # Check if user already exists
            if user_id in borrower_data:
                return "❌ User with this name and phone already exists", False
            
            # Calculate gold value (₹8000 per gram)
            gold_value = gold_grams * 8000
            
            # Create comprehensive borrower profile
            borrower_profile = {
                # Core Information
                "full_name": full_name,
                "phone_number": phone_number,
                "email": email,
                "password_hash": self.hash_password(password),
                "age": age,
                "gender": gender,
                "preferred_language": preferred_language,
                "aadhaar_number": aadhaar_number,
                "voter_id": voter_id,
                "marital_status": marital_status,
                "number_of_dependents": number_of_dependents,
                
                # Location
                "village_name": village_name,
                "district": district,
                "state": state,
                "pincode": pincode,
                "house_type": house_type,
                "electricity_connection": electricity_connection,
                
                # Occupation & Income
                "primary_occupation": primary_occupation,
                "secondary_income_sources": secondary_income_sources,
                "employment_type": employment_type,
                "seasonal_variation": seasonal_variation,
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "savings_per_month": savings_per_month,
                
                # Financial Profile
                "bank_account_status": bank_account_status,
                "bank_name": bank_name,
                "existing_loans": existing_loans,
                "repayment_history": repayment_history,
                "group_membership": group_membership,
                "past_loan_amounts": past_loan_amounts,
                
                # Digital Profile
                "owns_smartphone": owns_smartphone,
                "knows_how_to_use_apps": knows_how_to_use_apps,
                "preferred_mode_of_communication": preferred_mode_of_communication,
                "internet_availability": internet_availability,
                "digital_transaction_history": digital_transaction_history,
                "utility_bill_payments": utility_bill_payments,
                
                # Government & Social
                "government_scheme_eligibility": government_scheme_eligibility,
                
                # Assets
                "owns_land": owns_land,
                "land_area_text": land_area_text,
                "land_type": land_type,
                "patta_or_katha_number": patta_or_katha_number,
                "property_location": property_location,
                "land_area": land_area,
                "gold_grams": gold_grams,
                "gold_value_rupees": gold_value,
                "livestock_ownership": livestock_ownership,
                "vehicle_ownership": vehicle_ownership,
                
                # Notes
                "user_notes": user_notes,
                "agent_observations": agent_observations,
                
                # System Fields
                "registration_date": datetime.now().isoformat(),
                "profile_completed": True,
                "kyc_status": "pending",
                "loans": [],
                "payments": []
            }
            
            # Calculate credit score using fixed logic
            credit_score = self.calculate_credit_score(borrower_profile)
            borrower_profile["credit_score"] = credit_score
            
            # Get risk category
            risk_category, approval_rec = self.get_risk_category(credit_score)
            borrower_profile["risk_category"] = risk_category
            borrower_profile["approval_recommendation"] = approval_rec
            
            # Save data
            borrower_data[user_id] = borrower_profile
            self.save_borrower_data(borrower_data)
            
            return f"✅ Registration successful! Welcome {full_name}! Your credit score is {credit_score}/900 ({risk_category}). Total asset value: ₹{gold_value + (land_area * 100000):,.0f}.", True
            
        except Exception as e:
            return f"❌ Registration failed: {str(e)}", False
    
    def login_borrower(self, name: str, phone: str, password: str) -> Tuple[str, bool]:
        """Login borrower with session management"""
        try:
            user_id = self.generate_user_id(name, phone)
            borrower_data = self.load_borrower_data()
            
            if user_id not in borrower_data:
                return "❌ User not found. Please register first.", False
            
            user = borrower_data[user_id]
            if user["password_hash"] != self.hash_password(password):
                return "❌ Invalid password", False
            
            # Set current user for session management
            self.current_user = user_id
            
            return f"✅ Welcome back, {user['full_name']}! Your credit score: {user.get('credit_score', 650)}/900", True
            
        except Exception as e:
            return f"❌ Login failed: {str(e)}", False
    
    def get_borrower_profile(self) -> str:
        """Get current borrower's comprehensive profile"""
        if not self.current_user:
            return "❌ Please login first"
        
        borrower_data = self.load_borrower_data()
        user = borrower_data.get(self.current_user, {})
        
        if not user:
            return "❌ Profile not found"
        
        # Get credit score
        credit_score = user.get('credit_score', 0)
        risk_category = user.get('risk_category', 'Unknown')
        
        profile_html = f"""
# 👤 Comprehensive Borrower Profile

## 📋 Basic Information
**Name:** {user.get('full_name', 'N/A')}  
**Phone:** {user.get('phone_number', 'N/A')}  
**Email:** {user.get('email', 'N/A')}  
**Age:** {user.get('age', 'N/A')} years  
**Gender:** {user.get('gender', 'N/A').title()}  
**Marital Status:** {user.get('marital_status', 'N/A').title()}  
**Dependents:** {user.get('number_of_dependents', 'N/A')}  

## 📍 Location Details
**Village:** {user.get('village_name', 'N/A')}  
**District:** {user.get('district', 'N/A')}  
**State:** {user.get('state', 'N/A')}  
**Pincode:** {user.get('pincode', 'N/A')}  

## 💼 Occupation & Income
**Primary Occupation:** {user.get('primary_occupation', 'N/A')}  
**Monthly Income:** ₹{user.get('monthly_income', 0):,}  
**Monthly Expenses:** ₹{user.get('monthly_expenses', 0):,}  
**Savings per Month:** ₹{user.get('savings_per_month', 0):,}  
**Seasonal Variation:** {user.get('seasonal_variation', 'N/A').title()}  

## 🏦 Financial Profile
**Bank Account:** {user.get('bank_account_status', 'N/A').title()}  
**Existing Loans:** {user.get('existing_loans', 'N/A').title()}  
**Repayment History:** {user.get('repayment_history', 'N/A').title()}  
**Credit Score:** {credit_score}/900  
**Risk Category:** {risk_category}  

## 📊 Alternative Data Features
**Utility Bill Payments:** {user.get('utility_bill_payments', 'N/A').title()}  
**Digital Transactions:** {user.get('digital_transaction_history', 'N/A').title()}  
**Smartphone Usage:** {user.get('owns_smartphone', 'N/A').title()}  
**Internet Access:** {user.get('internet_availability', 'N/A').title()}  

## 🏛️ Government Scheme Features
**Scheme Eligibility:** {user.get('government_scheme_eligibility', 'N/A').title()}  

## 🏠 Asset Information
**Land Ownership:** {user.get('owns_land', 'N/A').title()}  
**Livestock Ownership:** {user.get('livestock_ownership', 'N/A').title()}  
**Vehicle Ownership:** {user.get('vehicle_ownership', 'N/A').title()}  
**Gold Holdings:** {user.get('gold_grams', 0)} grams (₹{user.get('gold_value_rupees', 0):,})  

## 📱 Digital Literacy
**Smartphone Usage:** {user.get('owns_smartphone', 'N/A').title()}  
**Internet Access:** {user.get('internet_availability', 'N/A').title()}  
**Digital Payments:** {user.get('digital_transaction_history', 'N/A').title()}  

## 🔄 Platform Activity
**Registration Date:** {user.get('registration_date', 'N/A')[:10]}  
**Profile Status:** {"✅ Complete" if user.get('profile_completed') else "⚠️ Incomplete"}  
**KYC Status:** {user.get('kyc_status', 'N/A').title()}  
**Total Loans Applied:** {len(user.get('loans', []))}  
**Total Payments Made:** {len(user.get('payments', []))}  
"""
        
        return profile_html
    
    def get_credit_analysis(self) -> str:
        """Get comprehensive credit analysis for current borrower"""
        if not self.current_user:
            return "❌ Please login first"
        
        borrower_data = self.load_borrower_data()
        user = borrower_data.get(self.current_user, {})
        
        if not user:
            return "❌ Profile not found"
        
        credit_score = user.get('credit_score', 0)
        risk_category = user.get('risk_category', 'Unknown')
        approval_rec = user.get('approval_recommendation', 'Review Required')
        
        analysis_html = f"""
# 📊 Comprehensive Credit Analysis

## 🎯 Credit Score Assessment
**Credit Score:** {credit_score}/900  
**Risk Level:** {risk_category}  
**Approval Recommendation:** {approval_rec}  

### Credit Score Breakdown
Your score of {credit_score} puts you in the **{self.get_score_range(credit_score)}** category.

### Score Components Analysis
"""
        
        # Analyze score components
        age = user.get('age', 25)
        income = user.get('monthly_income', 0)
        savings_ratio = user.get('savings_per_month', 0) / max(user.get('monthly_income', 1), 1)
        
        analysis_html += f"""
**Age Factor:** {age} years - {"✅ Prime age group" if 25 <= age <= 55 else "⚠️ Consider age impact"}  
**Income Level:** ₹{income:,}/month - {"✅ Excellent income" if income >= 100000 else "✅ Good income" if income >= 50000 else "⚠️ Moderate income"}  
**Savings Behavior:** {savings_ratio*100:.1f}% of income - {"✅ Excellent saver" if savings_ratio >= 0.2 else "✅ Good saver" if savings_ratio >= 0.1 else "⚠️ Improve savings"}  
**Digital Activity:** {user.get('digital_transaction_history', 'N/A')} - {"✅ Strong digital footprint" if 'excellent' in user.get('digital_transaction_history', '').lower() else "⚠️ Improve digital usage"}  

## 💰 Loan Eligibility Assessment

### Small Loans (₹25,000 - ₹50,000)
**Eligibility:** {"✅ Highly Likely" if credit_score >= 650 else "⚠️ Review Required" if credit_score >= 600 else "❌ Unlikely"}  
**Interest Rate Range:** {"8-12%" if credit_score >= 750 else "12-15%" if credit_score >= 650 else "15-18%"}  

### Medium Loans (₹50,000 - ₹2,00,000)
**Eligibility:** {"✅ Likely" if credit_score >= 700 else "⚠️ Review Required" if credit_score >= 650 else "❌ Unlikely"}  
**Interest Rate Range:** {"10-14%" if credit_score >= 750 else "14-17%" if credit_score >= 650 else "17-20%"}  

### Large Loans (₹2,00,000+)
**Eligibility:** {"✅ Likely" if credit_score >= 750 else "⚠️ Review Required" if credit_score >= 700 else "❌ Unlikely"}  
**Interest Rate Range:** {"12-16%" if credit_score >= 750 else "16-20%" if credit_score >= 700 else "20%+"}  

## 📈 Score Improvement Plan

### Immediate Actions (Next 30 days)
"""
        
        # Personalized improvement suggestions
        suggestions = []
        if savings_ratio < 0.15:
            suggestions.append("💰 Increase monthly savings to 15%+ of income")
        if 'excellent' not in user.get('digital_transaction_history', '').lower():
            suggestions.append("📱 Increase digital transaction frequency")
        if 'on time' not in user.get('utility_bill_payments', '').lower():
            suggestions.append("⚡ Ensure all utility bills are paid on time")
        if user.get('bank_account_status', '').lower() != 'have account':
            suggestions.append("🏦 Open and maintain a bank account")
        
        for suggestion in suggestions[:3]:
            analysis_html += f"- {suggestion}\n"
        
        analysis_html += f"""

### Medium-term Goals (3-6 months)
- 📊 Build consistent financial behavior patterns
- 🏦 Establish relationships with formal financial institutions
- 📱 Maintain high digital transaction activity
- 💼 Document income sources properly

### Long-term Strategy (6-12 months)
- 🎯 Target credit score of 750+ for best rates
- 🏠 Build asset documentation for collateral
- 📈 Consider secured credit products
- 🤝 Join financial literacy programs

## 🎯 Optimal Loan Strategy
**Recommended First Loan:** ₹{min(income * 3, 100000):,}  
**Purpose:** {"Business expansion" if income >= 50000 else "Income generation"}  
**Tenure:** 12-18 months  
**Expected Rate:** {self.get_expected_rate(credit_score)}  

## 💡 Pro Tips
- Apply for loans when your score is 650+
- Smaller first loans help build credit history
- Joint applications can improve approval chances
- Group lending often has better terms for first-time borrowers
"""
        
        return analysis_html
    
    def get_score_range(self, score: float) -> str:
        """Get credit score range description"""
        if score >= 750:
            return "Excellent"
        elif score >= 700:
            return "Good"
        elif score >= 650:
            return "Fair"
        elif score >= 600:
            return "Poor"
        else:
            return "Very Poor"
    
    def get_expected_rate(self, score: float) -> str:
        """Get expected interest rate based on score"""
        if score >= 750:
            return "8-12% annually"
        elif score >= 700:
            return "12-15% annually"
        elif score >= 650:
            return "15-18% annually"
        else:
            return "18-24% annually"
    
    def chat_with_education_agent(self, message: str, chat_history: List) -> Tuple[List, str]:
        """Chat with educational agent"""
        if not self.current_user:
            return chat_history + [[message, "❌ Please login first to use this feature"]], ""
        
        try:
            message_lower = message.lower()
            
            if "credit score" in message_lower:
                bot_response = """🎯 **Credit Score Information**

Your credit score (300-900) shows lenders how likely you are to repay loans:

**Score Ranges:**
- **750-900 (Excellent)**: Best rates, easy approval
- **700-749 (Good)**: Good rates, likely approval  
- **650-699 (Fair)**: Moderate rates, review required
- **600-649 (Poor)**: High rates, conditions apply
- **300-599 (Very Poor)**: Difficult approval, very high rates

**Quick Tips to Improve:**
✅ Pay all bills on time consistently
✅ Use digital payments regularly
✅ Maintain good savings habits
✅ Keep bank account active
✅ Build employment history"""
            
            elif "loan" in message_lower and ("type" in message_lower or "types" in message_lower):
                bot_response = """💰 **Types of Loans for You**

**1. Microfinance Loans**
- Amount: ₹5,000 - ₹2,00,000
- Purpose: Income generation, small business
- Features: Group guarantee, flexible terms

**2. Personal Loans**
- Amount: ₹25,000 - ₹5,00,000
- Purpose: Any personal need
- Features: No collateral needed

**3. Business Loans**
- Amount: ₹50,000 - ₹10,00,000
- Purpose: Business expansion, equipment
- Features: Lower rates, longer tenure

**4. Gold Loans**
- Amount: Up to 75% of gold value
- Purpose: Quick cash needs
- Features: Instant approval, lowest rates

**5. Agricultural Loans**
- Amount: Based on land holding
- Purpose: Crop cultivation, equipment
- Features: Seasonal repayment, subsidies"""
            
            elif "improve" in message_lower and "score" in message_lower:
                borrower_data = self.load_borrower_data()
                user = borrower_data.get(self.current_user, {})
                current_score = user.get('credit_score', 650)
                
                bot_response = f"""📈 **Your Score Improvement Plan**

**Current Score:** {current_score}/900

**Immediate Actions (This Month):**
🎯 Start digital payments for daily expenses
🎯 Pay all utility bills before due date
🎯 Maintain minimum ₹5,000 in bank account
🎯 Use UPI for grocery/fuel payments

**Medium-term (3 months):**
📊 Build consistent income documentation
📊 Join a local Self-Help Group (SHG)
📊 Apply for a small secured loan
📊 Increase savings rate to 20% of income

**Expected Improvement:** +50 to +100 points in 6 months
**Target Score:** {min(current_score + 75, 850)}/900"""
            
            elif "document" in message_lower:
                bot_response = """📄 **Documents You'll Need**

**Identity Proof:**
✅ Aadhaar Card (mandatory)
✅ PAN Card (for loans >₹50,000)
✅ Voter ID Card

**Address Proof:**
✅ Aadhaar Card
✅ Utility bill (electricity/water)
✅ Ration Card

**Income Proof:**
✅ Salary slips (last 3 months)
✅ Bank statements (6 months)
✅ ITR (if filed)
✅ Business license (for self-employed)

**Asset Proof:**
✅ Property documents
✅ Vehicle RC
✅ Gold purchase receipts

**Pro Tip:** Keep all documents in digital format on your phone!"""
            
            else:
                bot_response = """🤖 **I'm here to help with financial education!**

I can help you with:
📊 Credit score understanding and improvement
💰 Types of loans and eligibility
📄 Documentation requirements
💡 Financial planning tips
🏦 Banking and digital payments
📈 Investment basics

**Quick Questions:**
- "How to improve my credit score?"
- "What types of loans can I get?"
- "What documents do I need?"
- "How do interest rates work?"

Ask me anything about personal finance! 💪"""
            
            chat_history.append([message, bot_response])
            return chat_history, ""
            
        except Exception as e:
            error_response = "I apologize, I'm having technical difficulties. Please try asking about credit scores, loans, or financial planning!"
            chat_history.append([message, error_response])
            return chat_history, ""

def create_borrower_interface():
    """Create the borrower-focused Gradio interface"""
    platform = BorrowerPlatform()
    
    with gr.Blocks(title="GramSetuAI - Borrower Platform", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🌾 GramSetuAI - Borrower Platform
        ### Complete Financial Solution for Rural & Urban Borrowers
        **Powered by AI • Credit Scoring • Financial Education**
        """)
        
        # State management
        current_page = gr.State("auth")
        
        with gr.Column() as auth_page:
            gr.Markdown("## 🔐 Login / Register")
            
            with gr.Tab("Login"):
                with gr.Row():
                    with gr.Column(scale=1):
                        login_name = gr.Textbox(label="Full Name", placeholder="Enter your full name")
                        login_phone = gr.Textbox(label="Phone Number", placeholder="Enter your 10-digit phone number")
                        login_password = gr.Textbox(label="Password", type="password", placeholder="Enter your password")
                        login_btn = gr.Button("🔑 Login", variant="primary", size="lg")
                        login_output = gr.Markdown()
            
            with gr.Tab("Register"):
                gr.Markdown("### Complete your profile for accurate credit scoring")
                
                with gr.Row():
                    with gr.Column():
                        # Basic Information
                        gr.Markdown("#### 📋 Basic Information")
                        reg_name = gr.Textbox(label="Full Name *", placeholder="As per Aadhaar")
                        reg_phone = gr.Textbox(label="Phone Number *", placeholder="10-digit mobile number")
                        reg_email = gr.Textbox(label="Email Address *", placeholder="your.email@gmail.com")
                        reg_password = gr.Textbox(label="Password *", type="password", placeholder="Create a strong password")
                        
                        with gr.Row():
                            reg_age = gr.Number(label="Age *", value=25, minimum=18, maximum=80)
                            reg_gender = gr.Dropdown(["Male", "Female", "Other"], label="Gender *")
                            reg_marital = gr.Dropdown(["Single", "Married", "Divorced", "Widowed"], label="Marital Status")
                            reg_dependents = gr.Number(label="Number of Dependents", value=0, minimum=0)
                        
                        # Identity Documents
                        gr.Markdown("#### 🆔 Identity Documents")
                        with gr.Row():
                            reg_aadhaar = gr.Textbox(label="Aadhaar Number", placeholder="12-digit Aadhaar number")
                            reg_voter_id = gr.Textbox(label="Voter ID", placeholder="Voter ID number (optional)")
                            reg_preferred_language = gr.Dropdown(["English", "Hindi", "Kannada", "Tamil", "Telugu", "Marathi", "Bengali", "Gujarati"], label="Preferred Language")
                    
                    with gr.Column():
                        # Location Details
                        gr.Markdown("#### 📍 Location Details")
                        reg_village = gr.Textbox(label="Village/City *", placeholder="Your village or city name")
                        reg_district = gr.Textbox(label="District *", placeholder="Your district name")
                        reg_state = gr.Textbox(label="State *", placeholder="Your state name")
                        reg_pincode = gr.Textbox(label="Pincode *", placeholder="6-digit pincode")
                        
                        with gr.Row():
                            reg_house_type = gr.Dropdown(["Own House", "Rented", "Family Property", "Other"], label="House Type")
                            reg_electricity = gr.Dropdown(["Yes", "No", "Irregular"], label="Electricity Connection")
                
                with gr.Row():
                    with gr.Column():
                        # Occupation & Income
                        gr.Markdown("#### 💼 Occupation & Income")
                        reg_occupation = gr.Textbox(label="Primary Occupation *", placeholder="e.g., Farmer, Engineer, Business Owner")
                        reg_secondary_income = gr.Textbox(label="Secondary Income Sources", placeholder="Any additional income sources")
                        reg_employment_type = gr.Dropdown(["Self-employed", "Salaried", "Daily Wage", "Business Owner", "Farmer"], label="Employment Type")
                        reg_seasonal_variation = gr.Dropdown(["High", "Medium", "Low", "None"], label="Seasonal Income Variation")
                        
                        with gr.Row():
                            reg_income = gr.Number(label="Monthly Income (₹) *", value=25000, minimum=0)
                            reg_expenses = gr.Number(label="Monthly Expenses (₹)", value=15000, minimum=0)
                            reg_savings = gr.Number(label="Monthly Savings (₹)", value=5000, minimum=0)
                    
                    with gr.Column():
                        # Financial Profile
                        gr.Markdown("#### 🏦 Financial Profile")
                        reg_bank_account = gr.Dropdown(["Have Account", "No Account", "Multiple Accounts"], label="Bank Account Status")
                        reg_bank_name = gr.Textbox(label="Bank Name", placeholder="Primary bank name")
                        reg_existing_loans = gr.Dropdown(["None", "Personal Loan", "Business Loan", "Multiple Loans"], label="Existing Loans")
                        reg_repayment_history = gr.Dropdown(["New Borrower", "Excellent", "Good", "Average", "Poor"], label="Repayment History")
                        reg_group_membership = gr.Dropdown(["None", "SHG Member", "Cooperative Member", "Multiple Groups"], label="Group Membership")
                        reg_past_loan_amounts = gr.Textbox(label="Past Loan Amounts", placeholder="Previous loan amounts if any")
                
                with gr.Row():
                    with gr.Column():
                        # Digital Profile
                        gr.Markdown("#### 📱 Digital Profile")
                        reg_smartphone = gr.Dropdown(["Yes", "No", "Basic Phone"], label="Owns Smartphone")
                        reg_app_usage = gr.Dropdown(["Expert", "Good", "Basic", "None"], label="App Usage Skills")
                        reg_communication_mode = gr.Dropdown(["WhatsApp", "SMS", "Voice Call", "In Person"], label="Preferred Communication")
                        reg_internet = gr.Dropdown(["Regular", "Occasional", "Limited", "None"], label="Internet Availability")
                        reg_digital_transactions = gr.Dropdown(["Excellent", "Good", "Average", "Poor", "None"], label="Digital Transaction History")
                        reg_utility_payments = gr.Dropdown(["Always On Time", "Mostly On Time", "Sometimes Late", "Often Late"], label="Utility Bill Payments")
                        reg_govt_schemes = gr.Dropdown(["Multiple", "Few", "One", "None"], label="Government Scheme Eligibility")
                    
                    with gr.Column():
                        # Asset Information
                        gr.Markdown("#### 🏠 Asset Information")
                        reg_owns_land = gr.Dropdown(["Both Agricultural & Residential", "Only Agricultural", "Only Residential", "None"], label="Land Ownership")
                        reg_land_area_text = gr.Textbox(label="Land Area Description", placeholder="e.g., 2 acres agricultural land")
                        reg_land_type = gr.Dropdown(["Agricultural", "Residential", "Commercial", "Mixed", "None"], label="Land Type")
                        reg_patta_number = gr.Textbox(label="Patta/Katha Number", placeholder="Property document number")
                        reg_property_location = gr.Textbox(label="Property Location", placeholder="Where is your property located")
                        
                        with gr.Row():
                            reg_land_size = gr.Number(label="Land Size (acres)", value=0, minimum=0)
                            reg_gold_grams = gr.Number(label="Gold Holdings (grams)", value=0, minimum=0)
                        
                        reg_livestock = gr.Dropdown(["Cattle", "Goats", "Poultry", "Multiple", "None"], label="Livestock Ownership")
                        reg_vehicle = gr.Dropdown(["Two Wheeler", "Four Wheeler", "Commercial Vehicle", "Multiple", "None"], label="Vehicle Ownership")
                
                with gr.Row():
                    reg_user_notes = gr.Textbox(label="Additional Information", placeholder="Any other information you'd like to share", lines=2)
                    reg_agent_observations = gr.Textbox(label="Agent Observations", placeholder="For agent use only", lines=2)
                
                register_btn = gr.Button("📝 Complete Registration", variant="primary", size="lg")
                register_output = gr.Markdown()
        
        with gr.Column(visible=False) as dashboard_page:
            gr.Markdown("## 🏠 Borrower Dashboard")
            
            with gr.Tabs() as dashboard_tabs:
                with gr.Tab("📊 My Profile"):
                    profile_display = gr.Markdown()
                    refresh_profile_btn = gr.Button("🔄 Refresh Profile", variant="secondary")
                
                with gr.Tab("📈 Credit Analysis"):
                    credit_analysis_display = gr.Markdown()
                    refresh_analysis_btn = gr.Button("🔄 Refresh Analysis", variant="secondary")
                
                with gr.Tab("📚 Financial Education"):
                    gr.Markdown("### 🎓 Ask our AI Financial Advisor")
                    education_chatbot = gr.Chatbot(label="Financial Education Assistant", height=400)
                    education_input = gr.Textbox(label="Ask anything about finance, loans, or money management", placeholder="e.g., How can I improve my credit score?")
                    education_send = gr.Button("📤 Send", variant="primary")
                    education_clear = gr.Button("🗑️ Clear Chat", variant="secondary")
            
            logout_btn = gr.Button("🚪 Logout", variant="secondary")
        
        # Event handlers
        def handle_login(name, phone, password):
            result, success = platform.login_borrower(name, phone, password)
            if success:
                return result, gr.update(visible=False), gr.update(visible=True), "dashboard"
            return result, gr.update(), gr.update(), "auth"
        
        def handle_register(name, phone, email, password, age, gender, marital, dependents,
                           aadhaar, voter_id, preferred_language, village, district, state, pincode,
                           house_type, electricity, occupation, secondary_income, employment_type,
                           seasonal_variation, income, expenses, savings, bank_account, bank_name,
                           existing_loans, repayment_history, group_membership, past_loan_amounts,
                           smartphone, app_usage, communication_mode, internet, digital_transactions,
                           utility_payments, govt_schemes, owns_land, land_area_text, land_type,
                           patta_number, property_location, land_size, gold_grams, livestock,
                           vehicle, user_notes, agent_observations):
            result, success = platform.register_borrower(
                name, phone, email, password, age, gender, preferred_language, aadhaar, voter_id,
                marital, dependents, village, district, state, pincode, house_type, electricity,
                occupation, secondary_income, employment_type, seasonal_variation, income, expenses,
                savings, bank_account, bank_name, existing_loans, repayment_history, group_membership,
                past_loan_amounts, smartphone, app_usage, communication_mode, internet,
                digital_transactions, utility_payments, govt_schemes, owns_land, land_area_text,
                land_type, patta_number, property_location, land_size, gold_grams,
                livestock, vehicle, user_notes, agent_observations
            )
            if success:
                return result, gr.update(visible=False), gr.update(visible=True), "dashboard"
            return result, gr.update(), gr.update(), "auth"
        
        def handle_logout():
            platform.current_user = None
            return gr.update(visible=True), gr.update(visible=False), "auth"
        
        def refresh_profile():
            return platform.get_borrower_profile()
        
        def refresh_analysis():
            return platform.get_credit_analysis()
        
        def handle_education_chat(message, history):
            return platform.chat_with_education_agent(message, history)
        
        # Connect events
        login_btn.click(
            handle_login,
            inputs=[login_name, login_phone, login_password],
            outputs=[login_output, auth_page, dashboard_page, current_page]
        )
        
        register_btn.click(
            handle_register,
            inputs=[reg_name, reg_phone, reg_email, reg_password, reg_age, reg_gender, reg_marital, reg_dependents,
                   reg_aadhaar, reg_voter_id, reg_preferred_language, reg_village, reg_district, reg_state, reg_pincode,
                   reg_house_type, reg_electricity, reg_occupation, reg_secondary_income, reg_employment_type,
                   reg_seasonal_variation, reg_income, reg_expenses, reg_savings, reg_bank_account, reg_bank_name,
                   reg_existing_loans, reg_repayment_history, reg_group_membership, reg_past_loan_amounts,
                   reg_smartphone, reg_app_usage, reg_communication_mode, reg_internet, reg_digital_transactions,
                   reg_utility_payments, reg_govt_schemes, reg_owns_land, reg_land_area_text, reg_land_type,
                   reg_patta_number, reg_property_location, reg_land_size, reg_gold_grams, reg_livestock,
                   reg_vehicle, reg_user_notes, reg_agent_observations],
            outputs=[register_output, auth_page, dashboard_page, current_page]
        )
        
        logout_btn.click(
            handle_logout,
            outputs=[auth_page, dashboard_page, current_page]
        )
        
        refresh_profile_btn.click(
            refresh_profile,
            outputs=[profile_display]
        )
        
        refresh_analysis_btn.click(
            refresh_analysis,
            outputs=[credit_analysis_display]
        )
        
        education_send.click(
            handle_education_chat,
            inputs=[education_input, education_chatbot],
            outputs=[education_chatbot, education_input]
        )
        
        education_clear.click(
            lambda: ([], ""),
            outputs=[education_chatbot, education_input]
        )
        
        # Auto-load profile and analysis when dashboard opens
        dashboard_page.load(
            lambda: [platform.get_borrower_profile(), platform.get_credit_analysis()],
            outputs=[profile_display, credit_analysis_display]
        )
    
    return app

if __name__ == "__main__":
    print("🚀 Starting GramSetuAI Borrower Platform...")
    app = create_borrower_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )
