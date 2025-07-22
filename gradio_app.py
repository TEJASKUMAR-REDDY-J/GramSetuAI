#!/usr/bin/env python3
"""
Gradio Interface for Microfinance Agents System
Simple dashboard for user onboarding, credit scoring, and loan recommendations
"""

import gradio as gr
import json
import os
import sys
from typing import Dict, Any, Optional, Tuple

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.user_onboarding_agent import UserOnboardingAgent
from agents.credit_scoring_agent import CreditScoringAgent
from agents.loan_risk_advisor_agent import LoanRiskAdvisorAgent
from agents.educational_content_agent import EducationalContentAgent
from agents.document_processing_agent import DocumentProcessingAgent
from agents.voice_assistant_agent import VoiceAssistantAgent
from agents.translation_agent import TranslationAgent

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

def update_language_preference(new_language: str) -> str:
    """Update user's preferred language"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected"
    
    try:
        user_data = user_database[current_user_id]
        result = onboarding_agent.update_preferred_language(user_data, new_language.lower())
        
        if result["success"]:
            user_database[current_user_id] = result["updated_data"]
            save_user_data()
            return f"✅ {result['confirmation_message']}"
        else:
            return "❌ Failed to update language preference"
            
    except Exception as e:
        return f"❌ Error updating language preference: {e}"

def update_user_info(gender, marital_status, dependents, aadhaar, voter_id, age,
                    village, district, state, pincode, house_type, electricity,
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
    
    # Location Information
    if village: flattened_data["village_name"] = village
    if district: flattened_data["district"] = district
    if state: flattened_data["state"] = state
    if pincode: flattened_data["pincode"] = pincode
    if house_type: flattened_data["house_type"] = house_type
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
        
        # Get rule-based credit score
        rule_score = credit_agent.calculate_credit_score(user_data, "rule_based")
        
        # Get AI-backed score
        ai_score = credit_agent.calculate_credit_score(user_data, "ai_backed")
        
        result += f"""
## 🔢 Rule-Based Score
- **Credit Score**: {rule_score.get('credit_score', 'N/A')}/100
- **Risk Level**: {rule_score.get('risk_level', 'Unknown')}
- **Recommendation**: {rule_score.get('recommendation', 'N/A')}

### Factor Breakdown:
"""
        
        for factor, score in rule_score.get('factor_scores', {}).items():
            result += f"- **{factor.replace('_', ' ').title()}**: {score}/100\n"
        
        result += f"""
## 🤖 AI-Backed Score
- **Credit Score**: {ai_score.get('credit_score', 'N/A')}/100
- **Risk Assessment**: {ai_score.get('risk_level', 'N/A')}

## 🎯 Key Risk Factors
"""
        
        for factor in rule_score.get('key_risk_factors', [])[:3]:
            result += f"- {factor}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error calculating credit score: {e}"

def get_loan_recommendation() -> str:
    """Get detailed loan recommendation"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected"
    
    user_data = user_database[current_user_id]
    
    try:
        # Get credit result first
        credit_result = credit_agent.calculate_rule_based_score(user_data)
        
        # Get detailed loan recommendation
        recommendation = loan_advisor.provide_detailed_loan_recommendation(
            user_data, credit_result, None, "english"
        )
        
        loan_rec = recommendation.get('loan_recommendation', {})
        risk_analysis = recommendation.get('detailed_risk_analysis', {})
        summary = recommendation.get('final_summary', {})
        
        result = f"""
# 🏦 Loan Recommendation

## 📋 Decision Summary
- **Decision**: {loan_rec.get('decision', 'Unknown')}
- **Maximum Loan Amount**: ₹{loan_rec.get('maximum_loan_amount', 'N/A')}
- **Interest Rate**: {loan_rec.get('interest_rate_suggestion', 'N/A')}%
- **Repayment Period**: {loan_rec.get('repayment_period', 'N/A')} months
- **Collateral**: {loan_rec.get('collateral_requirement', 'N/A')}

## 📊 Risk Analysis
- **Risk Score**: {risk_analysis.get('overall_risk_score', 'N/A')}/100
- **Risk Category**: {risk_analysis.get('risk_category', 'Unknown').title()}

## 🎯 Key Risk Factors
"""
        
        for factor in risk_analysis.get('key_risk_factors', [])[:3]:
            result += f"- **{factor.get('factor', 'N/A')}** ({factor.get('impact', 'unknown')} impact)\n"
            result += f"  - {factor.get('explanation', 'No explanation')}\n"
        
        if summary.get('executive_summary'):
            result += f"\n## 📝 Executive Summary\n{summary['executive_summary']}"
        
        return result
        
    except Exception as e:
        return f"❌ Error generating loan recommendation: {e}"

def get_financial_education(topic: str) -> str:
    """Get financial education content"""
    global current_user_id
    
    if not current_user_id:
        return "❌ No user selected"
    
    user_data = user_database[current_user_id]
    
    try:
        if topic == "Credit Score Explanation":
            # Get current credit score first
            credit_result = credit_agent.calculate_rule_based_score(user_data)
            
            explanation = education_agent.explain_credit_score(
                credit_result, user_data, "english"
            )
            
            return f"# 📚 Credit Score Explanation\n\n{explanation}"
            
        elif topic == "Improvement Advice":
            credit_result = credit_agent.calculate_rule_based_score(user_data)
            
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
            gr.Markdown("#### 🏠 Location & Housing")
            with gr.Row():
                village_input = gr.Textbox(label="Village Name", placeholder="Enter village name")
                district_input = gr.Textbox(label="District", placeholder="Enter district")
                state_input = gr.Textbox(label="State", placeholder="Enter state", value="Karnataka")
            
            with gr.Row():
                pincode_input = gr.Textbox(label="Pincode", placeholder="6-digit pincode")
                house_type_input = gr.Dropdown(choices=["own", "rented", "family"], label="House Type")
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
            loan_btn = gr.Button("Get Loan Recommendation", variant="primary")
            loan_result = gr.Markdown()
        
        with gr.TabItem("📚 Financial Education"):
            gr.Markdown("### Financial Literacy Content")
            education_topic = gr.Dropdown(
                choices=["Credit Score Explanation", "Improvement Advice", "Seasonal Tips", "General Education"],
                label="Select Topic",
                value="Credit Score Explanation"
            )
            education_btn = gr.Button("Get Educational Content", variant="primary")
            education_result = gr.Markdown()
        
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
        outputs=[language_status]
    ).then(
        fn=lambda: get_user_dashboard(current_user_id) if current_user_id else "",
        outputs=[user_dashboard]
    )
    
    update_btn.click(
        fn=update_user_info,
        inputs=[gender_input, marital_status_input, dependents_input, aadhaar_input, voter_id_input, age_input,
                village_input, district_input, state_input, pincode_input, house_type_input, electricity_input,
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
    
    loan_btn.click(
        fn=get_loan_recommendation,
        outputs=[loan_result]
    )
    
    education_btn.click(
        fn=get_financial_education,
        inputs=[education_topic],
        outputs=[education_result]
    )
    
    chat_btn.click(
        fn=chat_with_assistant,
        inputs=[chat_message, chat_language],
        outputs=[chat_result, chat_audio]
    ).then(
        fn=lambda: "",
        outputs=[chat_message]
    )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        debug=False
    )
