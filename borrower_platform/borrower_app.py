#!/usr/bin/env python3
"""
Gradio Interface for Microfinance Agents System
Simple dashboard for user onboarding, credit scoring, and loan recommendations
"""

import gradio as gr
import json
import os
import sys
from typing import Dict, Any, Optional, Tuple, Tuple

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from agents.user_onboarding_agent import UserOnboardingAgent
from agents.credit_scoring_agent import CreditScoringAgent
from agents.loan_risk_advisor_agent import LoanRiskAdvisorAgent
from agents.educational_content_agent import EducationalContentAgent
from agents.document_processing_agent import DocumentProcessingAgent
from agents.voice_assistant_agent import VoiceAssistantAgent
from agents.translation_agent import TranslationAgent

# Import shared loan database
try:
    from shared_data.loan_database import loan_db
except ImportError:
    print("Warning: Shared loan database not available")
    loan_db = None

# Import RAG chat system
try:
    from shared_data.simple_rag_system import get_simple_rag_system
    rag_system = get_simple_rag_system()
    if rag_system:
        print("Simple RAG system initialized successfully")
    else:
        print("RAG system not available")
except ImportError:
    print("Warning: RAG chat system not available")
    rag_system = None

# Global state for user data
user_database = {}
current_user_id = None

# Initialize agents
onboarding_agent = UserOnboardingAgent()
credit_agent = CreditScoringAgent()
loan_advisor = LoanRiskAdvisorAgent()
education_agent = EducationalContentAgent()
document_agent = DocumentProcessingAgent()
voice_agent = VoiceAssistantAgent()
translation_agent = TranslationAgent()

def load_user_data():
    """Load existing user data from file"""
    global user_database
    try:
        if os.path.exists("user_data.json"):
            with open("user_data.json", "r", encoding="utf-8") as f:
                user_database = json.load(f)
    except Exception as e:
        print(f"Error loading user data: {e}")
        user_database = {}

def save_user_data():
    """Save user data to file"""
    try:
        with open("user_data.json", "w", encoding="utf-8") as f:
            json.dump(user_database, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving user data: {e}")

def get_user_list():
    """Get list of existing users"""
    if not user_database:
        return ["No users found"]
    return list(user_database.keys())

def create_new_user(name: str, phone: str, village: str) -> Tuple[str, str]:
    """Create a new user profile with standardized data structure"""
    global current_user_id
    
    if not name or not phone:
        return "❌ Name and phone number are required", ""
    
    user_id = f"{name}_{phone}"
    current_user_id = user_id
    
    # Initialize user data with flattened structure matching the standardized schema
    user_database[user_id] = {
        # Basic information provided during creation
        "full_name": name,
        "phone_number": phone,
        "village_name": village or "",
        "preferred_language": "english",
        
        # Initialize all other fields as empty/None to avoid missing field errors
        "age": None,
        "gender": "",
        "aadhaar_number": "",
        "marital_status": "",
        "voter_id": "",
        "district": "",
        "state": "",
        "pincode": "",
        "house_type": "",
        "electricity_connection": "",
        "number_of_dependents": None,
        "primary_occupation": "",
        "secondary_income_sources": "",
        "monthly_income": None,
        "monthly_expenses": None,
        "seasonal_variation": "",
        "bank_account_status": "",
        "bank_name": "",
        "existing_loans": "",
        "repayment_history": "",
        "savings_per_month": None,
        "group_membership": "",
        "past_loan_amounts": "",
        "owns_land": "",
        "land_area": "",
        "land_type": "",
        "patta_or_katha_number": "",
        "property_location": "",
        "owns_smartphone": "",
        "knows_how_to_use_apps": "",
        "preferred_mode_of_communication": "",
        "internet_availability": "",
        "user_notes": "",
        "agent_observations": ""
    }
    
    save_user_data()
    
    return f"✅ User {name} created successfully!", get_user_dashboard(user_id)

def select_existing_user(user_id: str) -> str:
    """Select an existing user"""
    global current_user_id
    
    if user_id == "No users found":
        return "❌ No users available"
    
    current_user_id = user_id
    return get_user_dashboard(user_id)

def get_user_dashboard(user_id: str) -> str:
    """Generate user dashboard"""
    if user_id not in user_database:
        return "❌ User not found"
    
    user_data = user_database[user_id]
    
    dashboard = f"""
# 👤 User Dashboard: {user_data.get('full_name', 'Unknown')}

## 📋 Basic Information
- **Name**: {user_data.get('full_name', 'Not provided')}
- **Phone**: {user_data.get('phone_number', 'Not provided')}
- **Age**: {user_data.get('age', 'Not provided')}
- **Gender**: {user_data.get('gender', 'Not provided')}
- **Village**: {user_data.get('village_name', 'Not provided')}
- **District**: {user_data.get('district', 'Not provided')}
- **Preferred Language**: {user_data.get('preferred_language', 'english').title()}

## 💼 Occupation & Income
- **Primary Occupation**: {user_data.get('primary_occupation', 'Not provided')}
- **Monthly Income**: ₹{user_data.get('monthly_income', 'Not provided')}
- **Monthly Expenses**: ₹{user_data.get('monthly_expenses', 'Not provided')}
- **Seasonal Variation**: {user_data.get('seasonal_variation', 'Not provided')}
- **Savings per Month**: ₹{user_data.get('savings_per_month', 'Not provided')}

## 🏦 Financial Information
- **Bank Account**: {user_data.get('bank_account_status', 'Not provided')}
- **Repayment History**: {user_data.get('repayment_history', 'Not provided')}
- **Group Membership**: {user_data.get('group_membership', 'Not provided')}

## 🏡 Property & Assets
- **Owns Land**: {user_data.get('owns_land', 'Not provided')}
- **Land Area**: {user_data.get('land_area', 'Not provided')}
- **Land Type**: {user_data.get('land_type', 'Not provided')}

## 📊 Profile Completeness
{get_profile_completeness(user_data)}

## 🎯 Available Actions
Use the tabs below to:
- Complete profile information
- Get credit score assessment
- Apply for loan recommendations
- Access financial education content
"""
    
    return dashboard

def get_profile_completeness(user_data: Dict) -> str:
    """Calculate and display profile completeness"""
    validation = onboarding_agent.validate_completeness(user_data)
    completeness = validation.get("completeness_score", 0)
    
    if completeness >= 80:
        status = "🟢 Complete"
    elif completeness >= 50:
        status = "🟡 Partial"
    else:
        status = "🔴 Incomplete"
    
    missing_fields = validation.get("missing_required_fields", [])
    missing_count = len(missing_fields)
    
    return f"{status} ({completeness}% complete, {missing_count} missing fields)"

def update_language_preference(new_language: str) -> tuple:
    """Update user's preferred language and refresh all interface elements"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected", get_user_dashboard()
    
    # Validate language input
    valid_languages = ["english", "hindi", "kannada"]
    if new_language.lower() not in valid_languages:
        return f"❌ Invalid language. Please select from: {', '.join(valid_languages)}", get_user_dashboard()
    
    try:
        user_data = user_database[current_user_id]
        
        # Ensure translator is available
        if not hasattr(onboarding_agent, 'translator'):
            return "❌ Translation service not available", get_user_dashboard()
        
        result = onboarding_agent.update_preferred_language(user_data, new_language.lower())
        
        if result.get("success"):
            user_database[current_user_id] = result["updated_data"]
            save_user_data()
            
            # Refresh dashboard with new language
            updated_dashboard = get_user_dashboard()
            
            # Create multilingual status message
            status_messages = {
                "english": f"✅ Language updated to {new_language}. All responses will now be in {new_language}.",
                "hindi": f"✅ भाषा {new_language} में अपडेट की गई। अब सभी जवाब {new_language} में होंगे।",
                "kannada": f"✅ ಭಾಷೆಯನ್ನು {new_language} ಗೆ ಅಪ್‌ಡೇಟ್ ಮಾಡಲಾಗಿದೆ। ಈಗ ಎಲ್ಲಾ ಉತ್ತರಗಳು {new_language} ನಲ್ಲಿ ಇರುತ್ತವೆ।"
            }
            
            status_message = status_messages.get(new_language.lower(), status_messages["english"])
            
            return status_message, updated_dashboard
        else:
            error_msg = result.get("error", "Unknown error")
            return f"❌ Failed to update language preference: {error_msg}", get_user_dashboard()
            
    except Exception as e:
        return f"❌ Error updating language preference: {e}", get_user_dashboard()

def update_user_info(gender, marital_status, dependents, aadhaar, voter_id, age,
                    house_number, street, landmark, village, taluk, district, state, pincode, police_station, house_ownership, house_construction, electricity,
                    occupation, secondary_income, income, expenses, seasonal_variation, savings_monthly,
                    bank_account, bank_name, existing_loans, repayment_history, past_loans, group_membership,
                    owns_land, land_area, land_type, patta_number, property_location,
                    smartphone, app_usage, communication_pref, internet,
                    user_notes, agent_observations) -> str:
    """Update complete user information with all standardized fields"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected"
    
    user_data = user_database[current_user_id]
    
    # Flatten the user data structure for easier field mapping
    flattened_data = {}
    
    # Personal Information
    if gender: flattened_data["gender"] = gender
    if marital_status: flattened_data["marital_status"] = marital_status
    if dependents is not None: flattened_data["number_of_dependents"] = int(dependents)
    if aadhaar: flattened_data["aadhaar_number"] = aadhaar
    if voter_id: flattened_data["voter_id"] = voter_id
    if age is not None: flattened_data["age"] = int(age)
    
    # Detailed Location Information
    if house_number: flattened_data["house_number"] = house_number
    if street: flattened_data["street"] = street
    if landmark: flattened_data["landmark"] = landmark
    if village: flattened_data["village_name"] = village
    if taluk: flattened_data["taluk"] = taluk
    if district: flattened_data["district"] = district
    if state: flattened_data["state"] = state
    if pincode: flattened_data["pincode"] = pincode
    if police_station: flattened_data["police_station"] = police_station
    if house_ownership: flattened_data["house_ownership"] = house_ownership
    if house_construction: flattened_data["house_type"] = house_construction
    if electricity: flattened_data["electricity_connection"] = electricity
    
    # Occupation & Income
    if occupation: flattened_data["primary_occupation"] = occupation
    if secondary_income: flattened_data["secondary_income_sources"] = secondary_income
    if income is not None: flattened_data["monthly_income"] = int(income)
    if expenses is not None: flattened_data["monthly_expenses"] = int(expenses)
    if seasonal_variation: flattened_data["seasonal_variation"] = seasonal_variation
    if savings_monthly is not None: flattened_data["savings_per_month"] = int(savings_monthly)
    
    # Financial Information
    if bank_account: flattened_data["bank_account_status"] = bank_account
    if bank_name: flattened_data["bank_name"] = bank_name
    if existing_loans: flattened_data["existing_loans"] = existing_loans
    if repayment_history: flattened_data["repayment_history"] = repayment_history
    if past_loans: flattened_data["past_loan_amounts"] = past_loans
    if group_membership: flattened_data["group_membership"] = group_membership
    
    # Property & Assets
    if owns_land: flattened_data["owns_land"] = owns_land
    if land_area: flattened_data["land_area"] = land_area
    if land_type: flattened_data["land_type"] = land_type
    if patta_number: flattened_data["patta_or_katha_number"] = patta_number
    if property_location: flattened_data["property_location"] = property_location
    
    # Digital Literacy
    if smartphone: flattened_data["owns_smartphone"] = smartphone
    if app_usage: flattened_data["knows_how_to_use_apps"] = app_usage
    if communication_pref: flattened_data["preferred_mode_of_communication"] = communication_pref
    if internet: flattened_data["internet_availability"] = internet
    
    # Additional Information
    if user_notes: flattened_data["user_notes"] = user_notes
    if agent_observations: flattened_data["agent_observations"] = agent_observations
    
    # Update the user data directly with flattened structure
    user_data.update(flattened_data)
    
    # Ensure full name and phone number from creation are preserved
    if "full_name" not in user_data and "name" in user_data:
        user_data["full_name"] = user_data["name"]
    if "phone_number" not in user_data and "phone" in user_data:
        user_data["phone_number"] = user_data["phone"]
    
    # Set preferred language if not set
    if "preferred_language" not in user_data:
        user_data["preferred_language"] = "english"
    
    save_user_data()
    
    return f"✅ Profile updated successfully!\n\n{get_user_dashboard(current_user_id)}"

def get_credit_score() -> str:
    """Calculate and display credit score with completeness check"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected"
    
    user_data = user_database[current_user_id]
    
    try:
        # Check data completeness first
        completeness = credit_agent.check_data_completeness(user_data)
        
        result = f"""
# 📊 Credit Score Assessment

## 📋 Data Completeness
- **Profile Completeness**: {completeness['completeness_percentage']}%
- **Fields Provided**: {completeness['provided_fields']}/{completeness['total_fields']}
- **Missing Fields**: {completeness['missing_fields']}

"""
        
        # Only calculate score if sufficient data is available
        if completeness['completeness_percentage'] < 60:
            result += f"""
⚠️ **Insufficient Data for Accurate Scoring**

Missing critical fields: {', '.join(completeness['missing_field_names'][:10])}

Please complete your profile to get an accurate credit assessment.

## 📚 How Our Credit Scoring Works

{credit_agent.explain_credit_scoring_system(user_data)}
"""
            return result
        
        # Get ML-based credit score (uses dynamic model weights)
        credit_result = credit_agent.calculate_credit_score(user_data, "rule_based")
        
        result += f"""
## � Credit Score Assessment
- **Credit Score**: {credit_result.get('credit_score', 'N/A')}/900
- **Risk Level**: {credit_result.get('risk_level', 'Unknown')}
- **Recommendation**: {credit_result.get('recommendation', 'N/A')}
- **Model Status**: {credit_result.get('scoring_method', 'Unknown')} with ML Model Weights

### Factor Breakdown (ML Model Weights):
"""
        
        # Get current model weights for display
        model_weights = credit_agent.scoring_weights
        for factor, score in credit_result.get('factor_scores', {}).items():
            weight = model_weights.get(factor, 0)
            factor_name = factor.replace('_', ' ').title()
            result += f"- **{factor_name}**: {score:.1f}/100 (Weight: {weight:.1f}%)\n"
        
        result += f"""
## 🎯 Key Risk Factors
"""
        
        for factor in credit_result.get('key_risk_factors', [])[:3]:
            result += f"- {factor}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error calculating credit score: {e}"

def calculate_loan_eligibility(user_data: Dict[str, Any], credit_score: int) -> Dict[str, Any]:
    """
    Calculate comprehensive loan eligibility using proper banking methodology
    
    Args:
        user_data: User profile data
        credit_score: Credit score (300-900)
        
    Returns:
        Dict with loan eligibility details
    """
    # 1️⃣ Use Net Income, Not Gross
    monthly_income = user_data.get('monthly_income', 0) or 0
    monthly_expenses = user_data.get('monthly_expenses', 0) or 0
    
    # Estimate net income (assuming 20% tax + deductions for income > 50K)
    if monthly_income > 50000:
        net_monthly_income = monthly_income * 0.8  # 80% after tax
    else:
        net_monthly_income = monthly_income * 0.9  # 90% for lower income
    
    # 2️⃣ Calculate Available EMI Capacity
    # Max 40-50% of net income for total EMIs (using 45% as middle ground)
    max_emi_capacity = net_monthly_income * 0.45
    
    # Subtract existing EMIs/expenses
    existing_obligations = monthly_expenses if monthly_expenses > 0 else (net_monthly_income * 0.3)  # Assume 30% for living expenses
    available_emi = max_emi_capacity - (existing_obligations * 0.1)  # Only 10% of expenses as debt obligations
    
    # Safety buffer (10-20% for emergencies)
    safety_buffer = 0.15  # 15% buffer
    safe_emi_limit = available_emi * (1 - safety_buffer)
    
    # 3️⃣ Calculate Interest Rate Based on Credit Score
    if credit_score >= 750:
        interest_rate = 10.5  # Excellent credit
    elif credit_score >= 650:
        interest_rate = 12.0  # Good credit
    elif credit_score >= 550:
        interest_rate = 14.0  # Fair credit
    elif credit_score >= 450:
        interest_rate = 16.5  # Poor credit
    else:
        interest_rate = 18.0  # Very poor credit
    
    # 4️⃣ Income-Based Loan Calculation (EMI-driven approach)
    # Standard tenure options based on loan type
    tenure_years = 5  # Default 5 years for personal loans
    tenure_months = tenure_years * 12
    
    # Calculate maximum principal using EMI formula
    # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    # Rearranged: P = EMI * ((1+r)^n - 1) / (r * (1+r)^n)
    monthly_interest_rate = interest_rate / 100 / 12
    
    if monthly_interest_rate > 0:
        emi_factor = ((1 + monthly_interest_rate) ** tenure_months - 1) / (monthly_interest_rate * (1 + monthly_interest_rate) ** tenure_months)
        income_based_amount = int(safe_emi_limit * emi_factor)
    else:
        income_based_amount = int(safe_emi_limit * tenure_months)
    
    # 5️⃣ Calculate Collateral Value & LTV-Based Amount
    collateral_value = 0
    collateral_details = []
    
    # Land valuation (more conservative approach)
    owns_land = user_data.get('owns_land', '').lower()
    if owns_land in ['yes', 'y']:
        land_area = user_data.get('land_area', '')
        land_type = user_data.get('land_type', '').lower()
        
        if land_area:
            try:
                # Extract numeric value from land area
                area_num = float(''.join(filter(lambda x: x.isdigit() or x == '.', str(land_area))))
                area_str = str(land_area).lower()
                
                # Convert to acres if needed
                if "acre" in area_str:
                    acres = area_num
                elif "gunta" in area_str:
                    acres = area_num * 0.025  # 1 gunta = 0.025 acres
                elif "cent" in area_str:
                    acres = area_num * 0.01   # 1 cent = 0.01 acres
                else:
                    acres = area_num  # Assume acres
                
                # Conservative land valuation (market rate * 0.8 for bank valuation)
                district = user_data.get('district', '').lower()
                
                # Conservative rates per acre (bank valuation, not market)
                if "commercial" in land_type:
                    if any(city in district for city in ['bangalore', 'bengaluru']):
                        rate_per_acre = 3000000  # 30L per acre (conservative)
                    else:
                        rate_per_acre = 800000   # 8L per acre
                elif "residential" in land_type:
                    if any(city in district for city in ['bangalore', 'bengaluru']):
                        rate_per_acre = 2000000  # 20L per acre
                    else:
                        rate_per_acre = 500000   # 5L per acre
                else:  # Agricultural land
                    if any(city in district for city in ['bangalore', 'bengaluru']):
                        rate_per_acre = 800000   # 8L per acre
                    else:
                        rate_per_acre = 200000   # 2L per acre
                
                land_value = int(acres * rate_per_acre)
                collateral_value += land_value
                collateral_details.append(f"Land: {acres:.2f} acres of {land_type} land valued at ₹{land_value:,}")
                
            except:
                collateral_details.append("Land: Area specified but value could not be calculated")
    
    # Property valuation (conservative bank assessment)
    house_type = user_data.get('house_type', '').lower()
    district = user_data.get('district', '').lower()
    
    # Conservative property values (bank assessment, not market)
    base_values = {
        "pucca": 800000,       # 8L for pucca house
        "concrete": 1000000,   # 10L for concrete house  
        "semi": 400000,        # 4L for semi-pucca
        "kachcha": 150000,     # 1.5L for kachcha
    }
    
    # Location multipliers (conservative)
    location_multipliers = {
        "bangalore": 1.8,
        "mysore": 1.4,
        "hubli": 1.3,
        "belgaum": 1.3,
        "mangalore": 1.4,
    }
    
    if house_type:
        property_value = 400000  # Default value
        for house_key, base_value in base_values.items():
            if house_key in house_type:
                property_value = base_value
                break
        
        # Apply location multiplier
        city_multiplier = 1.0
        for city, multiplier in location_multipliers.items():
            if city in district:
                city_multiplier = multiplier
                break
        
        property_value = int(property_value * city_multiplier)
        collateral_value += property_value
        collateral_details.append(f"Property: {house_type.title()} house in {district.title()} valued at ₹{property_value:,}")
    
    # 6️⃣ Apply LTV (Loan-to-Value) Ratio
    # Conservative LTV ratios based on loan type
    ltv_ratio = 0.70  # 70% LTV for secured loans (conservative)
    collateral_based_loan = int(collateral_value * ltv_ratio) if collateral_value > 0 else 0
    
    # 7️⃣ Final Eligibility (Lower of Income-based and Collateral-based)
    # For secured loans, take minimum of both
    # For unsecured loans, rely primarily on income
    if collateral_value > 0:
        # Secured loan - take lower of income and collateral capacity
        final_loan_amount = min(income_based_amount, collateral_based_loan)
    else:
        # Unsecured loan - income-based with credit score adjustments
        credit_adjustment = 1.0
        if credit_score >= 750:
            credit_adjustment = 1.2  # 20% bonus for excellent credit
        elif credit_score < 650:
            credit_adjustment = 0.8  # 20% reduction for poor credit
        
        final_loan_amount = int(income_based_amount * credit_adjustment)
    
    # Apply reasonable caps
    final_loan_amount = max(10000, min(final_loan_amount, 10000000))  # Cap between 10K and 1 Crore
    
    return {
        "net_monthly_income": int(net_monthly_income),
        "available_emi": int(available_emi),
        "safe_emi_limit": int(safe_emi_limit),
        "interest_rate": interest_rate,
        "tenure_months": tenure_months,
        "income_based_amount": income_based_amount,
        "collateral_value": collateral_value,
        "collateral_based_loan": collateral_based_loan,
        "final_loan_amount": final_loan_amount,
        "collateral_details": collateral_details,
        "ltv_ratio": ltv_ratio,
        "methodology": "Conservative banking approach with EMI-driven calculation"
    }

def show_loan_eligibility() -> str:
    """Show comprehensive maximum loan eligibility with detailed asset breakdown"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected"

    user_data = user_database[current_user_id]
    
    try:
        # Get credit score
        credit_result = credit_agent.calculate_credit_score(user_data, "rule_based")
        credit_score = credit_result.get('credit_score', 300)
        
        # Calculate eligibility
        eligibility = calculate_loan_eligibility(user_data, credit_score)
        
        # Determine risk category
        risk_category = ""
        if credit_score >= 750:
            risk_category = "Very Low Risk"
        elif credit_score >= 650:
            risk_category = "Low Risk"
        elif credit_score >= 550:
            risk_category = "Medium Risk"
        elif credit_score >= 450:
            risk_category = "High Risk"
        else:
            risk_category = "Very High Risk"
        
        # Calculate additional financial metrics
        gross_income = user_data.get('monthly_income', 0)
        annual_income = gross_income * 12
        savings_capacity = eligibility['net_monthly_income'] - eligibility['safe_emi_limit']
        
        # Estimate total liquid savings (annual savings capacity)
        estimated_liquid_savings = savings_capacity * 12 if savings_capacity > 0 else 0
        
        # Calculate total financial capacity
        total_assets = eligibility['collateral_value'] + estimated_liquid_savings
        
        # Format collateral breakdown
        collateral_breakdown = ""
        if eligibility['collateral_details']:
            collateral_breakdown = "\n".join(['  • ' + detail for detail in eligibility['collateral_details']])
        else:
            collateral_breakdown = "  • No physical collateral provided"
        
        return f"""
# 💰 Your Complete Financial Assessment & Maximum Loan Eligibility

## � Personal Financial Profile
- **Monthly Income**: ₹{gross_income:,} (Gross) | ₹{eligibility['net_monthly_income']:,} (Net after tax)
- **Annual Income**: ₹{annual_income:,}
- **Credit Score**: {credit_score}/900 ⭐ **{risk_category}**
- **Expected Interest Rate**: {eligibility['interest_rate']:.1f}% per annum

## 🏦 Income-Based Loan Capacity (EMI Method)
### Monthly Cash Flow Analysis:
- **Net Monthly Income**: ₹{eligibility['net_monthly_income']:,}
- **Safe EMI Capacity**: ₹{eligibility['safe_emi_limit']:,} (45% of net income with 15% safety buffer)
- **Remaining for Living**: ₹{savings_capacity:,} per month
- **Loan Tenure**: {eligibility['tenure_months']} months ({eligibility['tenure_months']//12} years)

### **📊 Income-Based Maximum Loan**: ₹{eligibility['income_based_amount']:,}

## 🏠 Total Asset & Collateral Valuation
### Physical Assets Portfolio:
{collateral_breakdown}

### **🏡 Total Collateral Value**: ₹{eligibility['collateral_value']:,}
### **📋 Loan-to-Value (LTV)**: {eligibility['ltv_ratio']:.0%} (Conservative banking standard)
### **💎 Collateral-Based Loan Capacity**: ₹{eligibility['collateral_based_loan']:,}

### Collateral Details:
{chr(10).join(['- ' + detail for detail in eligibility['collateral_details']]) if eligibility['collateral_details'] else '- No collateral provided'}

## 💵 Additional Financial Strength
- **Annual Savings Capacity**: ₹{estimated_liquid_savings:,} (Emergency fund potential)
- **Total Asset Base**: ₹{total_assets:,} (Physical assets + Liquid savings potential)
- **Asset-to-Income Ratio**: {(total_assets / annual_income):.1f}x annual income

## 🎯 Final Loan Eligibility Assessment

### **🏆 MAXIMUM ELIGIBLE LOAN AMOUNT: ₹{eligibility['final_loan_amount']:,}**

### 📊 Eligibility Calculation Method:
- **Method Used**: {eligibility['methodology']}
- **Primary Factor**: {"Collateral-based" if eligibility['collateral_based_loan'] < eligibility['income_based_amount'] else "Income-based"} (Lower amount for safety)
- **Safety Approach**: Conservative lending to ensure repayment capacity

*Note: For secured loans, we take the lower of income-based and collateral-based amounts for conservative lending.*

## 💡 Your Financial Strengths
✅ **Income Stability**: ₹{gross_income:,} monthly income  
✅ **Credit Worthiness**: {credit_score}/900 credit score ({risk_category})  
✅ **Asset Security**: ₹{eligibility['collateral_value']:,} in collateral assets  
✅ **Repayment Capacity**: ₹{eligibility['safe_emi_limit']:,} safe EMI limit  
✅ **Financial Buffer**: ₹{savings_capacity:,} monthly surplus for emergencies  

## 📈 Loan Optimization Tips
💡 **To Increase Eligibility:**
- Improve credit score further (current: {credit_score}/900)
- Add more collateral assets if available
- Consider longer tenure to reduce EMI burden
- Show additional income sources if any

💡 **Smart Borrowing Strategy:**
- Borrow only what you need (not maximum eligible)
- Keep EMI under ₹{eligibility['safe_emi_limit']:,} for comfort
- Maintain emergency fund of 6-12 months expenses
- Choose loan type matching your actual need

## � Next Steps
1. **Select Loan Type**: Choose from Personal, Business, Agriculture, Housing, etc.
2. **Specify Amount**: Enter desired amount (up to ₹{eligibility['final_loan_amount']:,})
3. **State Purpose**: Clearly mention loan purpose for better terms
4. **Get Recommendations**: Click "Get Loan Recommendation" for lender options

*Note: Final approved amount may vary based on lender-specific policies, documentation, and verification.*
"""
    except Exception as e:
        return f"❌ Error calculating eligibility: {e}"


def get_loan_recommendation_with_inputs(loan_type: str, loan_amount: float, loan_purpose: str) -> Tuple[str, str]:
    """Get detailed loan recommendation with user-specified parameters"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected", ""
    
    if not loan_amount or loan_amount <= 0:
        return "❌ Please enter a valid loan amount", ""
    
    if not loan_purpose or not loan_purpose.strip():
        return "❌ Please specify the purpose of the loan", ""

    user_data = user_database[current_user_id]
    
    try:
        # Get ML-based credit result 
        credit_result = credit_agent.calculate_credit_score(user_data, "rule_based")
        credit_score = credit_result.get('credit_score', 300)
        
        # Calculate comprehensive loan eligibility
        eligibility = calculate_loan_eligibility(user_data, credit_score)
        
        # Check if requested amount is within eligibility
        max_eligible = eligibility["final_loan_amount"]
        if loan_amount > max_eligible:
            eligibility_warning = f"""
⚠️ **ELIGIBILITY WARNING**: Your requested amount (₹{loan_amount:,}) exceeds your maximum eligibility (₹{max_eligible:,}).
We recommend applying for the maximum eligible amount.
"""
            recommended_amount = max_eligible
        else:
            eligibility_warning = f"✅ **ELIGIBILITY CONFIRMED**: Your requested amount is within your eligibility limit."
            recommended_amount = loan_amount
        
        # Create loan request with user inputs (ensure all values are native Python types)
        loan_request = {
            "amount": float(recommended_amount),
            "purpose": str(loan_purpose.strip()),
            "tenure_months": int(24),  # Default, can be made configurable
            "type": str(loan_type)
        }
        
        # Ensure credit result contains only native Python types
        if credit_result:
            credit_result = {
                key: float(value) if isinstance(value, (int, float)) and key == 'credit_score' 
                else value for key, value in credit_result.items()
            }
        
        # Get comprehensive loan advice with lender recommendations
        recommendation = loan_advisor.get_comprehensive_loan_advice_with_lenders(
            user_data, loan_request, credit_result, "english"
        )
        
        risk_assessment = recommendation.get('risk_assessment', {})
        lender_recommendations = recommendation.get('lender_recommendations', {})
        map_html = recommendation.get('map_html', '')
        
        result = f"""
# 🏦 Loan Recommendation for {loan_type.replace('_', ' ').title()}

{eligibility_warning}

## 📋 Application Details
- **Loan Type**: {loan_type.replace('_', ' ').title()}
- **Requested Amount**: ₹{loan_amount:,}
- **Recommended Amount**: ₹{recommended_amount:,}
- **Purpose**: {loan_purpose}
- **Expected Interest Rate**: {eligibility['interest_rate']:.1f}% per annum
- **Recommended Tenure**: {loan_request['tenure_months']} months
- **Estimated EMI**: ₹{eligibility['safe_emi_limit']:,.0f} (within your safe limit)

## 📊 Credit Assessment
- **Credit Score**: {credit_score}/900
- **Risk Category**: {risk_assessment.get('risk_category', 'Unknown')}
- **Approval Status**: {recommendation.get('approval_recommendation', 'Unknown')}

## 💰 Professional Loan Eligibility Assessment
### Income-Based Calculation (EMI-Driven Approach)
- **Gross Monthly Income**: ₹{user_data.get('monthly_income', 0):,}
- **Net Monthly Income**: ₹{eligibility['net_monthly_income']:,} (after tax & deductions)
- **Available EMI Capacity**: ₹{eligibility['available_emi']:,} (45% of net income)
- **Safe EMI Limit**: ₹{eligibility['safe_emi_limit']:,} (with 15% safety buffer)
- **Income-Based Loan Amount**: ₹{eligibility['income_based_amount']:,}

### Collateral-Based Calculation
- **Total Collateral Value**: ₹{eligibility['collateral_value']:,} (conservative bank valuation)
- **Loan-to-Value Ratio**: {eligibility['ltv_ratio']:.0%} (conservative lending approach)
- **Collateral-Based Loan**: ₹{eligibility['collateral_based_loan']:,}

### Collateral Details:
{chr(10).join(['- ' + detail for detail in eligibility['collateral_details']]) if eligibility['collateral_details'] else '- No collateral provided (unsecured loan)'}

## � Banking Methodology Applied
- **Approach**: Conservative EMI-driven calculation
- **Safety Buffer**: 15% buffer for emergencies and income fluctuations
- **LTV Policy**: Maximum 70% of collateral value for secured loans
- **Final Amount**: Lower of income-capacity and collateral-based amount

## �🏪 Available Lenders
{lender_recommendations.get('summary', 'No lender information available')}

## 💬 Personalized Advice
{recommendation.get('loan_advice', 'No specific advice available')}

## 📋 Next Steps
Based on your {loan_type.replace('_', ' ')} loan request:
1. **Document Preparation**: Gather required documents for {loan_type.replace('_', ' ')} loans
2. **EMI Planning**: Ensure EMI fits comfortably within ₹{eligibility['safe_emi_limit']:,.0f} limit
3. **Lender Selection**: Compare offers from the recommended lenders
4. **Application Process**: Apply with your preferred lender
5. **Follow-up**: Maintain regular communication during processing

💡 **Banking Tip**: Your EMI should not exceed 45% of your net income for financial stability.
"""
        
        return result, map_html
        
    except Exception as e:
        return f"❌ Error generating loan recommendation: {e}", ""


def get_loan_recommendation() -> Tuple[str, str]:
    """Get detailed loan recommendation with lender map"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected", ""
    
    user_data = user_database[current_user_id]
    
    try:
        # Get ML-based credit result 
        credit_result = credit_agent.calculate_credit_score(user_data, "rule_based")
        credit_score = credit_result.get('credit_score', 300)
        
        # Calculate comprehensive loan eligibility
        eligibility = calculate_loan_eligibility(user_data, credit_score)
        
        # Determine loan type based on occupation
        occupation = user_data.get('primary_occupation', '').lower()
        if any(word in occupation for word in ['farm', 'agriculture', 'crop']):
            loan_type = 'agriculture'
            loan_purpose = 'agriculture'
        elif any(word in occupation for word in ['business', 'shop', 'trade']):
            loan_type = 'micro_business'
            loan_purpose = 'business expansion'
        else:
            loan_type = 'personal'
            loan_purpose = 'personal needs'
        
        # Create dynamic loan request
        loan_request = {
            "amount": eligibility["final_loan_amount"],
            "purpose": loan_purpose,
            "tenure_months": 24,
            "type": loan_type
        }
        
        # Get comprehensive loan advice with lender recommendations
        recommendation = loan_advisor.get_comprehensive_loan_advice_with_lenders(
            user_data, loan_request, credit_result, "english"
        )
        
        risk_assessment = recommendation.get('risk_assessment', {})
        lender_recommendations = recommendation.get('lender_recommendations', {})
        map_html = recommendation.get('map_html', '')
        
        result = f"""
# 🏦 Comprehensive Loan Recommendation

## 📋 Approval Status
- **Recommendation**: {recommendation.get('approval_recommendation', 'Unknown')}
- **Risk Category**: {risk_assessment.get('risk_category', 'Unknown').title()}
- **Credit Score**: {credit_score}/900

## 💰 Enhanced Loan Eligibility Assessment
### Income-Based Calculation
- **Monthly Income**: ₹{user_data.get('monthly_income', 0):,}
- **Income Multiplier**: {eligibility['income_multiplier']}x (based on credit score)
- **Income-Based Amount**: ₹{eligibility['income_based_amount']:,}

### Collateral-Based Calculation
- **Total Collateral Value**: ₹{eligibility['collateral_value']:,}
- **Loan-to-Value Ratio**: {eligibility['ltv_ratio']*100:.0f}%
- **Collateral-Based Loan**: ₹{eligibility['collateral_based_loan']:,}

### Collateral Details:
"""
        
        for detail in eligibility['collateral_details']:
            result += f"- {detail}\n"
        
        if not eligibility['collateral_details']:
            result += "- No collateral assets identified\n"
        
        result += f"""
### **Final Recommended Amount**: ₹{eligibility['final_loan_amount']:,}
- **Purpose**: {loan_purpose.title()}
- **Suggested Tenure**: {loan_request.get('tenure_months', 'N/A')} months

## 🏪 Available Lenders
"""
        
        if lender_recommendations and lender_recommendations.get('recommendations'):
            lenders = lender_recommendations['recommendations']
            total_found = lender_recommendations.get('total_lenders_found', len(lenders))
            search_radius = lender_recommendations.get('search_criteria', {}).get('final_search_radius_km', 'Unknown')
            
            result += f"Found **{total_found}** lenders within **{search_radius}km** radius:\n\n"
            
            # Show top 10 lenders
            for i, lender in enumerate(lenders[:10], 1):
                distance = lender.get('distance', 'Unknown')
                result += f"**{i}. {lender.get('name', 'N/A')}**\n"
                result += f"   - Distance: {distance} km\n"
                result += f"   - Location: {lender.get('regional_office', 'N/A')}\n"
                result += f"   - Type: {lender.get('classification', 'N/A')}\n"
                result += f"   - Loan Range: ₹{lender.get('min_loan_amount', 0):,} - ₹{lender.get('max_loan_amount', 0):,}\n\n"
                
            if lender_recommendations.get('lender_analysis'):
                result += f"## 💡 Lender Analysis\n{lender_recommendations['lender_analysis']}\n\n"
        else:
            result += "No lenders found in your area. Please check your location details.\n\n"
        
        result += f"## 💬 Personalized Advice\n{recommendation.get('loan_advice', 'No advice available.')}\n\n"
        
        result += "## 📋 Next Steps\n"
        for i, step in enumerate(recommendation.get('next_steps', []), 1):
            result += f"{i}. {step}\n"
        
        return result, map_html or ""
        
    except Exception as e:
        return f"❌ Error generating loan recommendation: {e}", ""

def get_financial_education(topic: str) -> str:
    """Get financial education content"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected"
    
    user_data = user_database[current_user_id]
    
    try:
        if topic == "Credit Score Explanation":
            # Get current ML-based credit score
            credit_result = credit_agent.calculate_credit_score(user_data, "rule_based")
            
            explanation = education_agent.explain_credit_score(
                credit_result, user_data, "english"
            )
            
            return f"# 📚 Credit Score Explanation\n\n{explanation}"
            
        elif topic == "Improvement Advice":
            credit_result = credit_agent.calculate_credit_score(user_data, "rule_based")
            
            advice = education_agent.provide_improvement_advice(
                credit_result, user_data, "english"
            )
            
            result = "# 💡 Improvement Advice\n\n"
            
            if advice.get('immediate_actions'):
                result += "## 🚀 Immediate Actions\n"
                for action in advice['immediate_actions']:
                    result += f"- **{action.get('action', 'N/A')}**\n"
                    result += f"  - {action.get('explanation', 'N/A')}\n"
            
            if advice.get('short_term_goals'):
                result += "\n## 🎯 Short-term Goals\n"
                for goal in advice['short_term_goals']:
                    result += f"- **{goal.get('goal', 'N/A')}**\n"
                    result += f"  - Benefit: {goal.get('benefit', 'N/A')}\n"
            
            return result
            
        elif topic == "Seasonal Tips":
            tips = education_agent.generate_seasonal_financial_tips(
                user_data, "Kharif", "english"
            )
            
            result = "# 🌾 Seasonal Financial Tips\n\n"
            for i, tip in enumerate(tips, 1):
                result += f"{i}. {tip}\n\n"
            
            return result
            
        else:
            content = education_agent.create_financial_education_content(
                "credit_score_basics", user_data, "english"
            )
            return f"# 📖 Financial Education\n\n{content}"
            
    except Exception as e:
        return f"❌ Error generating educational content: {e}"

def chat_with_assistant(message: str, language: str) -> tuple:
    """Chat with the voice assistant with improved multilingual support and audio generation"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected", None
    
    user_data = user_database[current_user_id]
    
    # Update user's preferred language if different
    current_lang = translation_agent.get_user_preferred_language(user_data)
    if current_lang != language.lower():
        user_data = translation_agent.update_user_preferred_language(user_data, language.lower())
        user_database[current_user_id] = user_data
        save_user_data()
    
    try:
        # Check if user is asking about credit scoring system
        if any(phrase in message.lower() for phrase in ["credit score work", "how does credit", "credit scoring", "how credit score"]):
            explanation = credit_agent.explain_credit_scoring_system(user_data)
            response_text = f"🤖 **Assistant ({language})**:\n\n{explanation}"
            
            # Generate audio for the explanation
            audio_result = voice_agent.text_to_speech(explanation, language.lower())
            audio_file = None
            if audio_result.get("success") and audio_result.get("audio_path"):
                audio_file = audio_result["audio_path"]
            
            return response_text, audio_file
        
        # Use the improved voice query processing
        response = voice_agent.process_voice_query(
            query_text=message,
            user_data=user_data,
            context="Microfinance customer inquiry",
            language=language.lower()
        )
        
        if response.get("success"):
            response_text = f"🤖 **Assistant ({language})**:\n\n{response.get('response_text', 'Unable to generate response')}"
            
            # Generate audio for the response
            audio_result = voice_agent.text_to_speech(response.get('response_text', ''), language.lower())
            audio_file = None
            if audio_result.get("success") and audio_result.get("audio_path"):
                audio_file = audio_result["audio_path"]
            
            return response_text, audio_file
        else:
            error_text = f"❌ Error: {response.get('error', 'Unknown error occurred')}"
            return error_text, None
        
    except Exception as e:
        error_text = f"❌ Error: {e}"
        return error_text, None

# === LOAN APPLICATION FUNCTIONS ===

def get_available_mfis() -> str:
    """Get list of available MFIs for loan applications"""
    if not loan_db:
        return "❌ Loan system not available"
    
    try:
        mfis = loan_db.get_available_mfis()
        if not mfis:
            return "ℹ️ No microfinance institutions are currently available for loan applications."
        
        mfi_list = "## 🏦 Available Microfinance Institutions\n\n"
        for mfi in mfis:
            products_str = ', '.join(mfi['products']) if mfi['products'] else 'Standard loans'
            
            # Get additional details from mfi_directory
            mfi_details = loan_db.mfi_directory.get(mfi['mfi_id'], {})
            contact = mfi_details.get('contact', 'Not provided')
            phone = mfi_details.get('phone', 'Not provided')
            email = mfi_details.get('email', 'Not provided')
            interest_rates = mfi_details.get('interest_rates', 'Not specified')
            
            mfi_list += f"""
### 🏢 {mfi['name']}
- **📍 Location**: {mfi['location']}
- **👤 Contact Person**: {contact}
- **📞 Phone**: {phone}
- **📧 Email**: {email}
- **💰 Loan Range**: ₹{mfi['min_loan']:,} - ₹{mfi['max_loan']:,}
- **📈 Interest Rates**: {interest_rates}
- **🏦 Products**: {products_str}

---
"""
        return mfi_list
    except Exception as e:
        return f"❌ Error loading MFIs: {e}"

def get_mfi_choices() -> list:
    """Get list of MFI names for dropdown"""
    if not loan_db:
        return ["Loan system not available"]
    
    try:
        mfis = loan_db.get_available_mfis()
        if not mfis:
            return ["No MFIs available"]
        
        return [mfi['name'] for mfi in mfis]
    except Exception as e:
        return [f"Error loading MFIs: {e}"]

def submit_loan_application(mfi_name: str, loan_amount: float, loan_purpose: str, tenure_months: int, collateral: str, guarantor_name: str, guarantor_phone: str) -> str:
    """Submit loan application to selected MFI"""
    global current_user_id
    
    if not current_user_id:
        return "❌ Please login first"
    
    if not loan_db:
        return "❌ Loan system not available"
    
    if not mfi_name or loan_amount <= 0:
        return "❌ Please fill all required fields"
    
    try:
        # Get user data
        user_data = user_database.get(current_user_id, {})
        if not user_data:
            return "❌ User profile not found"
        
        # Get credit score for application
        try:
            credit_result = credit_agent.calculate_credit_score(user_data, "rule_based")
            credit_score = max(300, min(900, credit_result.get('credit_score', 650)))
        except:
            credit_score = 650  # Default score
        
        user_data['credit_score'] = credit_score
        
        # Find MFI ID by name
        mfis = loan_db.get_available_mfis()
        mfi_id = None
        for mfi in mfis:
            if mfi['name'] == mfi_name:
                mfi_id = mfi['mfi_id']
                break
        
        if not mfi_id:
            return f"❌ MFI '{mfi_name}' not found"
        
        # Prepare loan details
        loan_details = {
            'amount': loan_amount,
            'purpose': loan_purpose,
            'tenure_months': tenure_months,
            'collateral': collateral,
            'guarantor': {
                'name': guarantor_name,
                'phone': guarantor_phone
            }
        }
        
        # Submit application
        app_id = loan_db.submit_loan_application(user_data, mfi_id, loan_details)
        
        if app_id:
            return f"""
✅ **Loan Application Submitted Successfully!**

**Application ID**: {app_id}
**MFI**: {mfi_name}
**Amount**: ₹{loan_amount:,.0f}
**Purpose**: {loan_purpose}
**Tenure**: {tenure_months} months

Your application is now under review. You will be notified once the MFI processes your application.

Please keep your Application ID for future reference.
"""
        else:
            return "❌ Failed to submit application. Please try again."
            
    except Exception as e:
        return f"❌ Error submitting application: {e}"

def view_loan_applications() -> str:
    """View all loan applications for current user"""
    global current_user_id
    
    if not current_user_id:
        return "❌ Please login first"
    
    if not loan_db:
        return "❌ Loan system not available"
    
    try:
        user_data = user_database.get(current_user_id, {})
        borrower_id = user_data.get('phone_number', '')
        
        if not borrower_id:
            return "❌ Phone number not found in profile"
        
        applications = loan_db.get_applications_for_borrower(borrower_id)
        
        if not applications:
            return "ℹ️ No loan applications found."
        
        app_list = "## 📋 Your Loan Applications\n\n"
        for app in applications:
            status_emoji = {
                'pending': '🕐',
                'approved': '✅',
                'rejected': '❌'
            }.get(app['status'], '❓')
            
            app_list += f"""
### {status_emoji} Application ID: {app['application_id']}
- **MFI**: {app.get('mfi_id', 'Unknown')}
- **Amount**: ₹{app['loan_amount']:,.0f}
- **Purpose**: {app['loan_purpose']}
- **Status**: {app['status'].title()}
- **Applied**: {app['application_date'][:10]}
"""
            
            if app['status'] == 'approved':
                app_list += f"- **Approved Amount**: ₹{app.get('approved_amount', 0):,.0f}\n"
                app_list += f"- **Interest Rate**: {app.get('interest_rate', 0)}%\n"
                app_list += f"- **EMI**: ₹{app.get('emi_amount', 0):,.0f}\n"
            elif app['status'] == 'rejected':
                app_list += f"- **Reason**: {app.get('rejection_reason', 'Not specified')}\n"
            
            app_list += "---\n"
        
        return app_list
        
    except Exception as e:
        return f"❌ Error loading applications: {e}"

def view_active_loans() -> str:
    """View active loans and EMI details"""
    global current_user_id
    
    if not current_user_id:
        return "❌ Please login first"
    
    if not loan_db:
        return "❌ Loan system not available"
    
    try:
        user_data = user_database.get(current_user_id, {})
        borrower_id = user_data.get('phone_number', '')
        
        if not borrower_id:
            return "❌ Phone number not found in profile"
        
        loans = loan_db.get_loan_status(borrower_id)
        
        if not loans:
            return "ℹ️ No active loans found."
        
        loan_list = "## 💳 Your Active Loans\n\n"
        for loan in loans:
            status_emoji = {
                'active': '🟢',
                'completed': '✅',
                'overdue': '🔴'
            }.get(loan['status'], '❓')
            
            loan_list += f"""
### {status_emoji} Loan ID: {loan['loan_id'][:12]}...
- **MFI**: {loan['mfi_name']}
- **Principal**: ₹{loan['principal_amount']:,.0f}
- **EMI Amount**: ₹{loan['emi_amount']:,.0f}
- **Outstanding**: ₹{loan['outstanding_balance']:,.0f}
- **Status**: {loan['status'].title()}
- **Payments Made**: {loan['payments_made']}
"""
            
            if loan['status'] == 'active' and loan['next_due_date']:
                loan_list += f"- **Next Due**: {loan['next_due_date'][:10]}\n"
            
            loan_list += "---\n"
        
        return loan_list
        
    except Exception as e:
        return f"❌ Error loading loans: {e}"

def pay_emi(loan_id_display: str, payment_date: str = None) -> str:
    """Pay EMI for selected loan"""
    global current_user_id
    
    if not current_user_id:
        return "❌ Please login first"
    
    if not loan_db:
        return "❌ Loan system not available"
    
    if not loan_id_display:
        return "❌ Please select a loan"
    
    try:
        # Extract full loan ID from display text
        user_data = user_database.get(current_user_id, {})
        borrower_id = user_data.get('phone_number', '')
        loans = loan_db.get_loan_status(borrower_id)
        
        # Find matching loan
        selected_loan_id = None
        for loan in loans:
            if loan['loan_id'].startswith(loan_id_display.split('...')[0]):
                selected_loan_id = loan['loan_id']
                break
        
        if not selected_loan_id:
            return "❌ Loan not found"
        
        # Process payment
        result = loan_db.pay_emi(selected_loan_id, payment_date)
        
        if result['success']:
            payment = result['payment_details']
            return f"""
✅ **EMI Payment Successful!**

**Payment ID**: {payment['payment_id']}
**EMI Amount**: ₹{payment['emi_amount']:,.0f}
**Principal**: ₹{payment['principal_component']:,.0f}
**Interest**: ₹{payment['interest_component']:,.0f}

**Outstanding Before**: ₹{payment['outstanding_before']:,.0f}
**Outstanding After**: ₹{payment['outstanding_after']:,.0f}

**Loan Status**: {result['status'].title()}
{f"**Next Due Date**: {result['next_due_date'][:10]}" if result.get('next_due_date') else "**Loan Completed!** 🎉"}
"""
        else:
            return f"❌ Payment failed: {result['message']}"
            
    except Exception as e:
        return f"❌ Error processing payment: {e}"

def get_loan_options_for_emi() -> list:
    """Get list of active loans for EMI payment dropdown"""
    global current_user_id
    
    if not current_user_id or not loan_db:
        return ["No loans available"]
    
    try:
        user_data = user_database.get(current_user_id, {})
        borrower_id = user_data.get('phone_number', '')
        loans = loan_db.get_loan_status(borrower_id)
        
        active_loans = [f"{loan['loan_id'][:12]}... - ₹{loan['emi_amount']:,.0f} EMI" 
                       for loan in loans if loan['status'] == 'active']
        
        return active_loans if active_loans else ["No active loans"]
    except:
        return ["Error loading loans"]

def get_rag_chat_response(message: str, history: list = None) -> str:
    """Get response from RAG chat system"""
    if not rag_system:
        return "📚 **Financial Education Assistant**\n\nI'm currently being set up to help you with financial questions. In the meantime, I can provide general guidance:\n\n• **Microfinance loans** are small loans designed for people without access to traditional banking\n• **Save regularly** - even small amounts add up over time\n• **Keep good records** of your income and expenses\n• **Build your credit history** by repaying loans on time\n\nPlease try again in a few moments as I learn more about financial topics!"
    
    try:
        response = rag_system.get_response(message, user_type="borrower")
        
        # Format response nicely
        formatted_response = f"📚 **Financial Education Assistant**\n\n{response}"
        
        return formatted_response
    except Exception as e:
        return f"📚 **Financial Education Assistant**\n\nI apologize, but I'm having some technical difficulties right now. Please try asking your question again.\n\n**Common topics I can help with:**\n• Loan applications and requirements\n• Savings and investment options\n• Government financial schemes\n• Financial planning and budgeting\n• Business loans and microfinance\n\nError: {str(e)}"

def get_suggested_questions() -> list:
    """Get suggested questions for the chat"""
    if rag_system:
        try:
            return rag_system.get_suggested_questions("borrower")
        except:
            pass
    
    return [
        "How do I apply for a microfinance loan?",
        "What documents do I need for a loan application?",
        "How can I improve my credit score?",
        "What are the different types of savings accounts?",
        "How do I start a small business with a loan?",
        "What government schemes are available for entrepreneurs?",
        "How do I plan my finances and create a budget?",
        "What is the difference between secured and unsecured loans?"
    ]

def get_mfi_names_for_dropdown() -> list:
    """Get MFI names for dropdown selection"""
    if not loan_db:
        return ["Loan system not available"]
    
    try:
        mfis = loan_db.get_available_mfis()
        if not mfis:
            return ["No MFIs available"]
        
        return [mfi['name'] for mfi in mfis]
    except Exception as e:
        return [f"Error: {e}"]

def refresh_mfi_data():
    """Refresh both MFI display and dropdown choices"""
    display_text = get_available_mfis()
    dropdown_choices = get_mfi_names_for_dropdown()
    
    # Return the display text and a Gradio update for the dropdown
    return display_text, gr.update(choices=dropdown_choices, value=None)

def submit_simple_loan_application(mfi_name: str, loan_amount: float, loan_purpose: str) -> str:
    """Submit simplified loan application"""
    global current_user_id
    
    if not current_user_id:
        return "❌ Please login first"
    
    if not loan_db:
        return "❌ Loan system not available"
    
    if not mfi_name or mfi_name in ["Please refresh MFI list first", "No MFIs available", "Loan system not available"]:
        return "❌ Please select a valid MFI"
    
    if not loan_amount or loan_amount <= 0:
        return "❌ Please enter a valid loan amount"
    
    try:
        # Get user data
        user_data = user_database.get(current_user_id, {})
        if not user_data:
            return "❌ User profile not found. Please complete your profile first."
        
        # Get credit score for application
        try:
            credit_result = credit_agent.calculate_credit_score(user_data, "rule_based")
            credit_score = max(300, min(900, credit_result.get('credit_score', 650)))
        except:
            credit_score = 650  # Default score
        
        user_data['credit_score'] = credit_score
        
        # Find MFI ID by name
        mfis = loan_db.get_available_mfis()
        mfi_id = None
        for mfi in mfis:
            if mfi['name'] == mfi_name:
                mfi_id = mfi['mfi_id']
                break
        
        if not mfi_id:
            return f"❌ MFI '{mfi_name}' not found"
        
        # Prepare simple loan details
        loan_details = {
            'amount': loan_amount,
            'purpose': loan_purpose,
            'tenure_months': 12,  # Default 12 months
            'collateral': '',
            'guarantor': {}
        }
        
        # Submit application
        app_id = loan_db.submit_loan_application(user_data, mfi_id, loan_details)
        
        if app_id:
            return f"""
✅ **Loan Application Submitted Successfully!**

**Application ID**: {app_id}
**MFI**: {mfi_name}
**Amount**: ₹{loan_amount:,.0f}
**Purpose**: {loan_purpose}
**Your Credit Score**: {credit_score}/900

Your application is now under review. You will be notified once the MFI processes your application.

📋 Check the "My Applications" tab to track your application status.
"""
        else:
            return "❌ Failed to submit application. Please try again."
            
    except Exception as e:
        return f"❌ Error submitting application: {e}"

# Load existing user data on startup
load_user_data()

# Create Gradio interface
with gr.Blocks(title="Microfinance Agents System", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🏦 Microfinance Agents System")
    gr.Markdown("Complete microfinance solution with user onboarding, credit scoring, and loan recommendations")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 👤 User Management")
            
            # User selection
            user_dropdown = gr.Dropdown(
                choices=get_user_list(),
                label="Select Existing User",
                value=None
            )
            
            select_btn = gr.Button("Select User", variant="secondary")
            
            gr.Markdown("### Or Create New User")
            new_name = gr.Textbox(label="Full Name", placeholder="Enter full name")
            new_phone = gr.Textbox(label="Phone Number", placeholder="10-digit mobile number")
            new_village = gr.Textbox(label="Village Name", placeholder="Village name (optional)")
            create_btn = gr.Button("Create New User", variant="primary")
            
            gr.Markdown("### 🌐 Language Preference")
            language_dropdown = gr.Dropdown(
                choices=["English", "Hindi", "Kannada"],
                label="Update Preferred Language",
                value="English"
            )
            language_btn = gr.Button("Update Language", variant="secondary")
            language_status = gr.Textbox(label="Language Status", interactive=False)
            
            user_status = gr.Textbox(label="Status", interactive=False)
        
        with gr.Column(scale=2):
            user_dashboard = gr.Markdown("## Select or create a user to view dashboard")
    
    with gr.Tabs():
        with gr.TabItem("📝 Complete Profile"):
            gr.Markdown("### Complete User Profile - All Fields Required for Accurate Credit Scoring")
            
            # Personal Information Section
            gr.Markdown("#### 👤 Personal Information")
            with gr.Row():
                gender_input = gr.Dropdown(choices=["male", "female", "other"], label="Gender")
                marital_status_input = gr.Dropdown(choices=["single", "married", "divorced", "widowed"], label="Marital Status")
                dependents_input = gr.Number(label="Number of Dependents", minimum=0, maximum=10, step=1)
            
            with gr.Row():
                aadhaar_input = gr.Textbox(label="Aadhaar Number", placeholder="12-digit Aadhaar number")
                voter_id_input = gr.Textbox(label="Voter ID", placeholder="Voter ID number")
                age_input = gr.Number(label="Age", minimum=18, maximum=100, step=1)
            
            # Location Information Section
            gr.Markdown("#### 🏠 Location & Housing (Detailed Address Required)")
            with gr.Row():
                house_number_input = gr.Textbox(label="House/Door Number", placeholder="Enter house number")
                street_input = gr.Textbox(label="Street/Road Name", placeholder="Enter street or road name")
                landmark_input = gr.Textbox(label="Landmark", placeholder="Near temple, school, etc.")
            
            with gr.Row():
                village_input = gr.Textbox(label="Village/Town Name", placeholder="Enter village or town name")
                taluk_input = gr.Textbox(label="Taluk/Tehsil", placeholder="Enter taluk or tehsil")
                district_input = gr.Textbox(label="District", placeholder="Enter district")
            
            with gr.Row():
                state_input = gr.Textbox(label="State", placeholder="Enter state", value="Karnataka")
                pincode_input = gr.Textbox(label="Pincode", placeholder="6-digit pincode")
                police_station_input = gr.Textbox(label="Nearest Police Station", placeholder="Police station name")
            
            with gr.Row():
                house_ownership_input = gr.Dropdown(choices=["own", "rented", "family", "ancestral"], label="House Ownership")
                house_construction_input = gr.Dropdown(choices=["pucca", "semi-pucca", "kachcha", "concrete"], label="House Construction Type")
                electricity_input = gr.Dropdown(choices=["yes", "no"], label="Electricity Connection")
            
            # Occupation & Income Section
            gr.Markdown("#### 💼 Occupation & Income")
            with gr.Row():
                occupation_input = gr.Textbox(label="Primary Occupation", placeholder="e.g., farmer, shopkeeper, laborer")
                secondary_income_input = gr.Textbox(label="Secondary Income Sources", placeholder="e.g., livestock, part-time work")
                income_input = gr.Number(label="Monthly Income (₹)", minimum=0, step=1000)
            
            with gr.Row():
                expenses_input = gr.Number(label="Monthly Expenses (₹)", minimum=0, step=1000)
                seasonal_variation_input = gr.Dropdown(choices=["high", "medium", "low", "none"], label="Seasonal Income Variation")
                savings_monthly_input = gr.Number(label="Savings per Month (₹)", minimum=0, step=500)
            
            # Financial Information Section
            gr.Markdown("#### 🏦 Banking & Financial History")
            with gr.Row():
                bank_account_input = gr.Dropdown(choices=["yes", "no"], label="Bank Account Status")
                bank_name_input = gr.Textbox(label="Bank Name", placeholder="Primary bank name")
                existing_loans_input = gr.Textbox(label="Existing Loans", placeholder="Details of current loans")
            
            with gr.Row():
                repayment_input = gr.Dropdown(choices=["excellent", "good", "fair", "poor", "no_history"], label="Repayment History")
                past_loans_input = gr.Textbox(label="Past Loan Amounts", placeholder="Previous loan amounts and purposes")
                group_membership_input = gr.Textbox(label="Group Membership", placeholder="SHG, cooperative, or community groups")
            
            # Property & Assets Section
            gr.Markdown("#### 🏡 Property & Assets")
            with gr.Row():
                owns_land_input = gr.Dropdown(choices=["yes", "no"], label="Owns Land")
                land_area_input = gr.Textbox(label="Land Area", placeholder="e.g., 2.5 acres, 1 hectare")
                land_type_input = gr.Dropdown(choices=["agricultural", "residential", "commercial", "barren"], label="Land Type")
            
            with gr.Row():
                patta_number_input = gr.Textbox(label="Patta/Katha Number", placeholder="Land document number")
                property_location_input = gr.Textbox(label="Property Location", placeholder="Location of main property")
                
            # Digital Literacy Section
            gr.Markdown("#### 📱 Digital Literacy")
            with gr.Row():
                smartphone_input = gr.Dropdown(choices=["yes", "no"], label="Owns Smartphone")
                app_usage_input = gr.Dropdown(choices=["expert", "basic", "beginner", "none"], label="App Usage Knowledge")
                communication_pref_input = gr.Dropdown(choices=["phone", "sms", "app", "in_person"], label="Preferred Communication")
            
            with gr.Row():
                internet_input = gr.Dropdown(choices=["always", "sometimes", "rarely", "never"], label="Internet Availability")
                
            # Additional Notes Section
            gr.Markdown("#### 📝 Additional Information")
            with gr.Row():
                user_notes_input = gr.Textbox(label="User Notes", placeholder="Any additional information", lines=2)
                agent_observations_input = gr.Textbox(label="Agent Observations", placeholder="Agent notes", lines=2)
            
            update_btn = gr.Button("Update Complete Profile", variant="primary", size="lg")
            update_status = gr.Markdown()
        
        with gr.TabItem("📊 Credit Score"):
            gr.Markdown("### Credit Score Assessment")
            credit_btn = gr.Button("Calculate Credit Score", variant="primary")
            credit_result = gr.Markdown()
        
        with gr.TabItem("🏦 Loan Recommendation"):
            gr.Markdown("### Loan Application Assessment")
            
            with gr.Row():
                loan_type_input = gr.Dropdown(
                    choices=["personal", "agriculture", "micro_business", "housing", "education", "vehicle", "gold_loan"],
                    label="Loan Type",
                    value="personal"
                )
                loan_amount_input = gr.Number(
                    label="Desired Loan Amount (₹)",
                    minimum=10000,
                    maximum=5000000,
                    step=10000,
                    value=500000
                )
            
            loan_purpose_input = gr.Textbox(
                label="Loan Purpose",
                placeholder="e.g., business expansion, home renovation, education, vehicle purchase"
            )
            
            with gr.Row():
                show_eligibility_btn = gr.Button("Show My Maximum Eligibility", variant="secondary")
                loan_btn = gr.Button("Get Loan Recommendation", variant="primary")
            
            eligibility_result = gr.Markdown()
            loan_result = gr.Markdown()
            gr.Markdown("### 🗺️ Nearby Lenders Map")
            lender_map = gr.HTML(label="Lender Locations")
        
        with gr.TabItem("📚 Financial Education Chat"):
            gr.Markdown("### 💬 AI-Powered Financial Assistant")
            gr.Markdown("*Ask me anything about loans, savings, investments, government schemes, and financial planning!*")
            
            # Chat interface
            with gr.Row():
                with gr.Column(scale=3):
                    financial_chatbot = gr.Chatbot(
                        label="Financial Education Assistant", 
                        height=400,
                        show_label=True,
                        bubble_full_width=False
                    )
                    
                    with gr.Row():
                        financial_msg = gr.Textbox(
                            label="Your Question",
                            placeholder="Ask about loans, savings, financial planning, government schemes...",
                            lines=2,
                            scale=4
                        )
                        financial_send_btn = gr.Button("Send", variant="primary", scale=1)
                    
                    financial_clear_btn = gr.Button("Clear Chat", variant="secondary")
                
                with gr.Column(scale=1):
                    gr.Markdown("### 💡 Suggested Questions")
                    suggested_questions_display = gr.Markdown()
            
            # Auto-populate suggested questions
            def load_suggested_questions():
                questions = get_suggested_questions()
                formatted = "\n".join([f"• {q}" for q in questions[:6]])
                return f"""**Click on any topic to get started:**

{formatted}

**Or ask your own question!**"""
            
            # Chat functionality
            def respond_to_financial_query(message, history):
                if not message.strip():
                    return history, ""
                
                # Get response from RAG system
                response = get_rag_chat_response(message)
                
                # Update history
                history = history or []
                history.append([message, response])
                
                return history, ""
            
            def clear_financial_chat():
                if rag_system:
                    try:
                        rag_system.clear_chat_history()
                    except:
                        pass
                return []
        
        with gr.TabItem("🤖 Voice Assistant"):
            gr.Markdown("### Chat with Assistant")
            
            with gr.Row():
                chat_message = gr.Textbox(label="Your Message", placeholder="Ask about loans, payments, or general help")
                chat_language = gr.Dropdown(choices=["English", "Hindi", "Kannada"], label="Language", value="English")
            
            chat_btn = gr.Button("Send Message", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    chat_result = gr.Markdown(label="Text Response")
                with gr.Column():
                    chat_audio = gr.Audio(label="Voice Response", autoplay=True)
        
        with gr.TabItem("🏦 Apply for Loan"):
            gr.Markdown("### Available Microfinance Institutions")
            
            refresh_mfi_btn = gr.Button("Refresh MFI List", variant="secondary")
            mfi_list_display = gr.Markdown()
            
            gr.Markdown("### Quick Loan Application")
            with gr.Row():
                mfi_selection = gr.Dropdown(
                    label="Select MFI", 
                    choices=["Please refresh MFI list first"],
                    value=None,
                    interactive=True,
                    allow_custom_value=False
                )
                loan_amount_simple = gr.Number(label="Loan Amount (₹)", minimum=5000, maximum=500000, value=50000)
            
            loan_purpose_simple = gr.Dropdown(
                label="Loan Purpose", 
                choices=["Business", "Agriculture", "Education", "Medical Emergency", "Home Improvement", "Other"],
                value="Business"
            )
            
            apply_loan_btn = gr.Button("Apply for Loan", variant="primary", size="lg")
            loan_application_result = gr.Markdown()
        
        with gr.TabItem("📋 My Applications"):
            gr.Markdown("### Your Loan Applications")
            
            refresh_applications_btn = gr.Button("Refresh Applications", variant="secondary")
            applications_display = gr.Markdown()
        
        with gr.TabItem("💳 My Loans & EMI"):
            gr.Markdown("### Active Loans")
            
            refresh_loans_btn = gr.Button("Refresh Loans", variant="secondary")
            loans_display = gr.Markdown()
            
            gr.Markdown("### Pay EMI")
            with gr.Row():
                loan_selection = gr.Dropdown(label="Select Loan", choices=["No loans available"])
                payment_date_input = gr.Textbox(label="Payment Date (Optional)", placeholder="YYYY-MM-DD or leave blank for today")
            
            pay_emi_btn = gr.Button("Pay EMI", variant="primary")
            payment_result = gr.Markdown()
    
    # Event handlers
    create_btn.click(
        fn=create_new_user,
        inputs=[new_name, new_phone, new_village],
        outputs=[user_status, user_dashboard]
    ).then(
        fn=lambda: get_user_list(),
        outputs=[user_dropdown]
    )
    
    select_btn.click(
        fn=select_existing_user,
        inputs=[user_dropdown],
        outputs=[user_dashboard]
    )
    
    language_btn.click(
        fn=update_language_preference,
        inputs=[language_dropdown],
        outputs=[language_status, user_dashboard]
    )
    
    update_btn.click(
        fn=update_user_info,
        inputs=[gender_input, marital_status_input, dependents_input, aadhaar_input, voter_id_input, age_input,
                house_number_input, street_input, landmark_input, village_input, taluk_input, district_input, state_input, pincode_input, police_station_input, house_ownership_input, house_construction_input, electricity_input,
                occupation_input, secondary_income_input, income_input, expenses_input, seasonal_variation_input, savings_monthly_input,
                bank_account_input, bank_name_input, existing_loans_input, repayment_input, past_loans_input, group_membership_input,
                owns_land_input, land_area_input, land_type_input, patta_number_input, property_location_input,
                smartphone_input, app_usage_input, communication_pref_input, internet_input,
                user_notes_input, agent_observations_input],
        outputs=[update_status]
    ).then(
        fn=lambda: get_user_dashboard(current_user_id) if current_user_id else "",
        outputs=[user_dashboard]
    )
    
    credit_btn.click(
        fn=get_credit_score,
        outputs=[credit_result]
    )
    
    show_eligibility_btn.click(
        fn=show_loan_eligibility,
        outputs=[eligibility_result]
    )
    
    loan_btn.click(
        fn=get_loan_recommendation_with_inputs,
        inputs=[loan_type_input, loan_amount_input, loan_purpose_input],
        outputs=[loan_result, lender_map]
    )
    
    # Financial Chat Event Handlers
    financial_send_btn.click(
        fn=respond_to_financial_query,
        inputs=[financial_msg, financial_chatbot],
        outputs=[financial_chatbot, financial_msg]
    )
    
    financial_msg.submit(
        fn=respond_to_financial_query,
        inputs=[financial_msg, financial_chatbot],
        outputs=[financial_chatbot, financial_msg]
    )
    
    financial_clear_btn.click(
        fn=clear_financial_chat,
        outputs=[financial_chatbot]
    )
    
    # Load suggested questions on startup
    app.load(
        fn=load_suggested_questions,
        outputs=[suggested_questions_display]
    )
    
    chat_btn.click(
        fn=chat_with_assistant,
        inputs=[chat_message, chat_language],
        outputs=[chat_result, chat_audio]
    ).then(
        fn=lambda: "",
        outputs=[chat_message]
    )
    
    # Loan application event handlers
    refresh_mfi_btn.click(
        fn=refresh_mfi_data,
        outputs=[mfi_list_display, mfi_selection]
    )
    
    apply_loan_btn.click(
        fn=submit_simple_loan_application,
        inputs=[mfi_selection, loan_amount_simple, loan_purpose_simple],
        outputs=[loan_application_result]
    )
    
    refresh_applications_btn.click(
        fn=view_loan_applications,
        outputs=[applications_display]
    )
    
    refresh_loans_btn.click(
        fn=view_active_loans,
        outputs=[loans_display]
    ).then(
        fn=get_loan_options_for_emi,
        outputs=[loan_selection]
    )
    
    pay_emi_btn.click(
        fn=pay_emi,
        inputs=[loan_selection, payment_date_input],
        outputs=[payment_result]
    ).then(
        # Refresh loan list after payment
        fn=view_active_loans,
        outputs=[loans_display]
    ).then(
        # Update loan dropdown options
        fn=get_loan_options_for_emi,
        outputs=[loan_selection]
    )

    # Load MFI data on startup
    app.load(
        fn=refresh_mfi_data,
        outputs=[mfi_list_display, mfi_selection]
    )
    
    # Auto-load MFI data when the app starts
    app.load(
        fn=refresh_mfi_data,
        outputs=[mfi_list_display, mfi_selection]
    )

    # Auto-load loan options for EMI payment
    app.load(
        fn=get_loan_options_for_emi,
        outputs=[loan_selection]
    )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        debug=False
    )
