"""
MFI Platform - Microfinance Institution Management System
Main Gradio interface for MFI operations and analytics
"""

import gradio as gr
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

sys.path.append(os.path.join(os.path.dirname(__file__), 'data'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lender_agents'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'borrower_platform'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Support both relative imports (when used as module) and direct imports (when run as script)
try:
    from .data.mfi_database import mfi_db
    from .lender_agents.creditsense_analyst import CreditSenseAnalyst
    from .lender_agents.fundflow_forecaster import FundFlowForecaster
    from .lender_agents.policypulse_advisor import PolicyPulseAdvisor
    from .lender_agents.opsgenie_agent import OpsGenieAgent
except ImportError:
    # Fallback to absolute imports when run as script
    from data.mfi_database import mfi_db
    from lender_agents.creditsense_analyst import CreditSenseAnalyst
    from lender_agents.fundflow_forecaster import FundFlowForecaster
    from lender_agents.policypulse_advisor import PolicyPulseAdvisor
    from lender_agents.opsgenie_agent import OpsGenieAgent

# Import shared loan database
try:
    from shared_data.loan_database import loan_db
except ImportError:
    print("Warning: Shared loan database not available")
    loan_db = None

# Import RAG chat system for lenders
try:
    from shared_data.simple_rag_system import get_simple_rag_system
    rag_system = get_simple_rag_system()
    if rag_system:
        print("Simple RAG system initialized successfully for MFI")
    else:
        print("RAG system not available for MFI")
except ImportError:
    print("Warning: RAG chat system not available")
    rag_system = None
try:
    from shared_data.loan_database import loan_db
except ImportError:
    print("Warning: Shared loan database not available")
    loan_db = None

# Global variables for session management
current_mfi_id = None
current_mfi_profile = None

# Initialize AI agents
try:
    credit_analyst = CreditSenseAnalyst()
    fundflow_forecaster = FundFlowForecaster()
    policy_advisor = PolicyPulseAdvisor()
    ops_agent = OpsGenieAgent()
except Exception as e:
    print(f"Warning: Some AI agents failed to initialize: {e}")
    credit_analyst = None
    fundflow_forecaster = None
    policy_advisor = None
    ops_agent = None

def login_mfi(mfi_selection: str) -> Tuple[str, bool]:
    """Handle MFI login using dropdown selection instead of username/password"""
    global current_mfi_id, current_mfi_profile
    
    if not mfi_selection or mfi_selection == "Select an MFI":
        return "❌ Please select an MFI from the dropdown", False
    
    try:
        # Extract MFI ID from selection (format: "MFI_ID - MFI_Name")
        if " - " in mfi_selection:
            selected_mfi_id = mfi_selection.split(" - ")[0]
        else:
            return "❌ Invalid MFI selection format", False
        
        # Get MFI profile from the shared database
        if not loan_db:
            return "❌ Database system not available", False
        
        # Load MFI directory to find the profile
        mfi_directory = loan_db.mfi_directory
        if selected_mfi_id not in mfi_directory:
            return f"❌ MFI {selected_mfi_id} not found in directory", False
        
        # Set current MFI context
        current_mfi_id = selected_mfi_id
        mfi_info = mfi_directory[selected_mfi_id]
        
        # Create a basic profile structure
        current_mfi_profile = {
            "basic_details": {
                "mfi_name": mfi_info.get('name', 'Unknown MFI'),
                "registration_number": selected_mfi_id,
                "entity_type": "NBFC-MFI",
                "year_establishment": 2022,
                "head_office_address": mfi_info.get('location', 'Not provided'),
                "operating_states": "Karnataka",
                "contact_person": {
                    "name": mfi_info.get('contact', 'Not provided'),
                    "role": "Manager",
                    "email": mfi_info.get('email', 'Not provided'),
                    "phone": mfi_info.get('phone', 'Not provided'),
                    "whatsapp": mfi_info.get('phone', 'Not provided')
                }
            },
            "operational_metrics": {
                "active_borrowers": 0,
                "loan_portfolio_size": 0.0,
                "average_loan_size": 0.0,
                "minimum_loan_amount": mfi_info.get('minimum_loan', 10000),
                "maximum_loan_amount": mfi_info.get('maximum_loan', 100000),
                "loan_products": ', '.join(mfi_info.get('loan_products', [])),
                "repayment_frequencies": "Monthly"
            },
            "financial_compliance": {
                "interest_rates": mfi_info.get('interest_rates', 'Not specified'),
                "portfolio_at_risk": 0.0
            },
            "target_segments": {
                "borrower_type_focus": "SHGs, Cooperative society, earning individuals, farmers, weavers, etc.",
                "sector_focus": "Agriculture, services, livestock",
                "geographies_covered": "Karnataka"
            }
        }
        
        mfi_name = current_mfi_profile["basic_details"]["mfi_name"]
        return f"✅ Welcome to {mfi_name} Dashboard!", True
        
    except Exception as e:
        return f"❌ Login error: {e}", False

def get_available_mfis_for_login() -> list:
    """Get list of MFIs for login dropdown"""
    try:
        if not loan_db:
            return ["Database not available"]
        
        mfi_directory = loan_db.mfi_directory
        if not mfi_directory:
            return ["No MFIs available"]
        
        # Format: "MFI_ID - MFI_Name"
        mfi_options = []
        for mfi_id, mfi_info in mfi_directory.items():
            mfi_name = mfi_info.get('name', 'Unknown MFI')
            mfi_options.append(f"{mfi_id} - {mfi_name}")
        
        return ["Select an MFI"] + mfi_options
        
    except Exception as e:
        return [f"Error loading MFIs: {e}"]

def register_new_mfi(
    # Basic Institution Details
    mfi_name: str,
    registration_number: str,
    entity_type: str,
    year_establishment: int,
    head_office_address: str,
    operating_states: str,
    contact_person_name: str,
    contact_person_role: str,
    contact_email: str,
    contact_phone: str,
    contact_whatsapp: str,
    
    # Operational Metrics
    active_borrowers: int,
    loan_portfolio_size: float,
    average_loan_size: float,
    min_loan_amount: float,
    max_loan_amount: float,
    loan_products: str,
    repayment_frequencies: str,
    
    # Team & Staff Info
    total_field_officers: int,
    branches_centers: int,
    ops_manager_contacts: str,
    training_process: str,
    
    # Technology Usage
    loan_management_software: str,
    digital_lending_tools: str,
    data_format: str,
    integration_preferences: str,
    
    # Financial & Compliance
    funding_sources: str,
    interest_rates: str,
    portfolio_at_risk: float,
    credit_bureau_integration: str,
    latest_audit_date: str,
    
    # Target Segments
    borrower_type_focus: str,
    sector_focus: str,
    loan_tenure_range: str,
    geographies_covered: str,
    
    # Goals & Challenges
    top_challenges: str,
    vision_next_2_years: str,
    support_needed: str,
    
    # Login credentials
    username: str,
    password: str
) -> str:
    """Register a new MFI"""
    
    if not all([mfi_name, registration_number, username, password]):
        return "❌ Please fill in all required fields (MFI Name, Registration Number, Username, Password)"
    
    # Structure the MFI data
    mfi_data = {
        "basic_details": {
            "mfi_name": mfi_name,
            "registration_number": registration_number,
            "entity_type": entity_type,
            "year_establishment": year_establishment,
            "head_office_address": head_office_address,
            "operating_states": operating_states,
            "contact_person": {
                "name": contact_person_name,
                "role": contact_person_role,
                "email": contact_email,
                "phone": contact_phone,
                "whatsapp": contact_whatsapp
            }
        },
        "operational_metrics": {
            "active_borrowers": active_borrowers,
            "loan_portfolio_size": loan_portfolio_size,
            "average_loan_size": average_loan_size,
            "minimum_loan_amount": min_loan_amount,
            "maximum_loan_amount": max_loan_amount,
            "loan_products": loan_products,
            "repayment_frequencies": repayment_frequencies
        },
        "team_staff": {
            "total_field_officers": total_field_officers,
            "branches_centers": branches_centers,
            "ops_manager_contacts": ops_manager_contacts,
            "training_process": training_process
        },
        "technology": {
            "loan_management_software": loan_management_software,
            "digital_lending_tools": digital_lending_tools,
            "data_format": data_format,
            "integration_preferences": integration_preferences
        },
        "financial_compliance": {
            "funding_sources": funding_sources,
            "interest_rates": interest_rates,
            "portfolio_at_risk": portfolio_at_risk,
            "credit_bureau_integration": credit_bureau_integration,
            "latest_audit_date": latest_audit_date
        },
        "target_segments": {
            "borrower_type_focus": borrower_type_focus,
            "sector_focus": sector_focus,
            "loan_tenure_range": loan_tenure_range,
            "geographies_covered": geographies_covered
        },
        "goals_challenges": {
            "top_challenges": top_challenges,
            "vision_next_2_years": vision_next_2_years,
            "support_needed": support_needed
        }
    }
    
    result = mfi_db.register_mfi(mfi_data, username, password)
    
    if result["success"]:
        return f"✅ MFI registered successfully! Your MFI ID: {result['mfi_id']}"
    else:
        return f"❌ Registration failed: {result['error']}"

def get_mfi_dashboard() -> str:
    """Generate MFI dashboard overview"""
    global current_mfi_profile
    
    if not current_mfi_profile:
        return "❌ Please log in first"
    
    basic = current_mfi_profile.get("basic_details", {})
    ops = current_mfi_profile.get("operational_metrics", {})
    
    return f"""
# 🏢 {basic.get('mfi_name', 'Unknown MFI')} - Dashboard

## 📊 Quick Overview
- **Registration Number**: {basic.get('registration_number', 'N/A')}
- **Entity Type**: {basic.get('entity_type', 'N/A')}
- **Operating Since**: {basic.get('year_establishment', 'N/A')}
- **Active Borrowers**: {ops.get('active_borrowers', 0):,}
- **Loan Portfolio**: ₹{ops.get('loan_portfolio_size', 0):,.2f}
- **Average Loan Size**: ₹{ops.get('average_loan_size', 0):,.2f}

## 🌍 Operations
- **Operating States**: {basic.get('operating_states', 'N/A')}
- **Loan Products**: {ops.get('loan_products', 'N/A')}
- **Repayment Frequency**: {ops.get('repayment_frequencies', 'N/A')}

## 👥 Contact Information
- **Contact Person**: {basic.get('contact_person', {}).get('name', 'N/A')} ({basic.get('contact_person', {}).get('role', 'N/A')})
- **Email**: {basic.get('contact_person', {}).get('email', 'N/A')}
- **Phone**: {basic.get('contact_person', {}).get('phone', 'N/A')}

## 🎯 Focus Areas
- **Target Segments**: {current_mfi_profile.get('target_segments', {}).get('borrower_type_focus', 'N/A')}
- **Primary Sectors**: {current_mfi_profile.get('target_segments', {}).get('sector_focus', 'N/A')}
- **Geographic Coverage**: {current_mfi_profile.get('target_segments', {}).get('geographies_covered', 'N/A')}
"""

def logout_mfi() -> Tuple[str, bool]:
    """Handle MFI logout"""
    global current_mfi_id, current_mfi_profile
    
    current_mfi_id = None
    current_mfi_profile = None
    
    return "👋 Logged out successfully!", False

def run_creditsense_analysis(borrower_id: str, recent_behavior: str, location: str, group_score: float) -> str:
    """Run CreditSense risk analysis"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please log in first to access analytics"
    
    if not credit_analyst:
        return "❌ CreditSense Analyst is not available"
    
    if not borrower_id:
        return "❌ Please enter a borrower ID for analysis"
    
    try:
        result = credit_analyst.generate_risk_report(
            borrower_id=borrower_id,
            recent_behavior=recent_behavior,
            location=location,
            group_score=group_score
        )
        return result
    except Exception as e:
        return f"❌ Error generating risk analysis: {str(e)}"

def run_fundflow_forecast(cash_position: float, regional_filter: str, months_ahead: int) -> str:
    """Run FundFlow cashflow forecast"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please log in first to access analytics"
    
    if not fundflow_forecaster:
        return "❌ FundFlow Forecaster is not available"
    
    try:
        result = fundflow_forecaster.generate_cashflow_forecast(
            mfi_id=current_mfi_id,
            cash_position=cash_position,
            regional_filter=regional_filter,
            months_ahead=int(months_ahead)
        )
        return result
    except Exception as e:
        return f"❌ Error generating cashflow forecast: {str(e)}"

def run_policy_pulse_scan(state: str, borrower_occupation: str) -> str:
    """Run PolicyPulse compliance and scheme scan"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please log in first to access analytics"
    
    if not policy_advisor:
        return "❌ PolicyPulse Advisor is not available"
    
    try:
        borrower_filters = {}
        if borrower_occupation:
            borrower_filters["occupation"] = borrower_occupation
        
        result = policy_advisor.generate_policy_pulse_report(
            mfi_id=current_mfi_id,
            state=state,
            borrower_filters=borrower_filters
        )
        return result
    except Exception as e:
        return f"❌ Error scanning policy updates: {str(e)}"

def run_creditsense_analysis(risk_filter: str, refresh_data: bool) -> str:
    """Run CreditSense portfolio analysis"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please log in first to access analytics"
    
    if not credit_analyst:
        return "❌ CreditSense Analyst is not available"
    
    try:
        result = credit_analyst.generate_portfolio_analysis(
            mfi_id=current_mfi_id,
            risk_threshold=risk_filter
        )
        return result
    except Exception as e:
        return f"❌ Error generating credit analysis: {str(e)}"

def update_borrower_performance(borrower_id: str, updated_by: str, performance_notes: str, risk_flag: str) -> str:
    """Update borrower performance data"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please log in first to update borrower data"
    
    if not credit_analyst:
        return "❌ CreditSense Analyst is not available"
    
    if not all([borrower_id, updated_by, performance_notes]):
        return "❌ Please fill in all required fields"
    
    try:
        performance_data = {
            'notes': performance_notes,
            'risk_flag': risk_flag
        }
        
        result = credit_analyst.update_borrower_performance(
            borrower_id=borrower_id,
            mfi_id=current_mfi_id,
            performance_data=performance_data,
            updated_by=updated_by
        )
        
        if result['success']:
            return f"✅ {result['message']}"
        else:
            return f"❌ {result['error']}"
            
    except Exception as e:
        return f"❌ Error updating borrower performance: {str(e)}"

def run_fundflow_forecast(regional_filter: str, months_ahead: int) -> str:
    """Run FundFlow cashflow forecast"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please log in first to access analytics"
    
    if not fundflow_forecaster:
        return "❌ FundFlow Forecaster is not available"
    
    try:
        result = fundflow_forecaster.generate_cashflow_forecast(
            mfi_id=current_mfi_id,
            months_ahead=months_ahead,
            regional_filter=regional_filter
        )
        return result
    except Exception as e:
        return f"❌ Error generating cashflow forecast: {str(e)}"

def generate_voice_response(query: str, borrower_id: str = "") -> Tuple[str, str]:
    """Generate voice response for MFI queries"""
    global current_mfi_id, current_mfi_profile
    
    if not current_mfi_id:
        return "❌ Please log in first to access voice assistant", ""
    
    try:
        # Create comprehensive prompt for voice response
        prompt = f"""
You are an AI voice assistant for microfinance institutions in India. Respond in a conversational, professional tone as if speaking to an MFI manager.

MFI CONTEXT:
- MFI ID: {current_mfi_id}
- MFI Name: {current_mfi_profile.get('basic_details', {}).get('mfi_name', 'Unknown')}
- Active Borrowers: {current_mfi_profile.get('operational_metrics', {}).get('active_borrowers', 'N/A')}
- Portfolio Size: ₹{current_mfi_profile.get('operational_metrics', {}).get('loan_portfolio_size', 0):,}

QUERY: {query}
SPECIFIC BORROWER: {borrower_id if borrower_id else 'None specified'}

Provide a helpful, conversational response about:
- Portfolio performance insights
- Risk management advice  
- Operational recommendations
- Borrower-specific information if ID provided

Keep response under 200 words, professional but conversational for voice delivery.
"""

        from groq import Groq
        client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        
        response = client.chat.completions.create(
            model=os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        voice_text = response.choices[0].message.content.strip()
        
        # Format for display
        formatted_response = f"""
# 🎤 Voice Assistant Response

**Query**: {query}  
**MFI**: {current_mfi_profile.get('basic_details', {}).get('mfi_name', 'Unknown')}  
**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 🗣️ Response:

{voice_text}

---
*Use the 'Play Audio' button to hear this response (Text-to-Speech)*
"""
        
        return formatted_response, voice_text
        
    except Exception as e:
        error_msg = f"❌ Error generating voice response: {str(e)}"
        return error_msg, ""

def run_opsgenie_report(zone_filter: str, fo_filter: str, max_visits: int) -> str:
    """Run OpsGenie operations analysis"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please log in first to access analytics"
    
    if not ops_agent:
        return "❌ OpsGenie Agent is not available"
    
    try:
        result = ops_agent.generate_weekly_ops_report(
            mfi_id=current_mfi_id,
            zone_filter=zone_filter
        )
        return result
    except Exception as e:
        return f"❌ Error generating operations report: {str(e)}"

# === LOAN APPLICATION MANAGEMENT FUNCTIONS ===

def view_pending_applications() -> str:
    """View all pending loan applications for the current MFI"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please login first"
    
    if not loan_db:
        return "❌ Loan system not available"
    
    try:
        applications = loan_db.get_applications_for_mfi(current_mfi_id)
        pending_apps = [app for app in applications if app['status'] == 'pending']
        
        if not pending_apps:
            return "ℹ️ No pending applications found."
        
        app_list = f"## 📋 Pending Loan Applications ({len(pending_apps)})\n\n"
        
        for app in pending_apps:
            app_list += f"""
### 📄 Application ID: {app['application_id']}
**Borrower**: {app['borrower_name']} ({app['borrower_id']})  
**Amount Requested**: ₹{app['loan_amount']:,.0f}  
**Purpose**: {app['loan_purpose']}  
**Tenure**: {app['loan_tenure']} months  
**Applied**: {app['application_date'][:10]}  
**Credit Score**: {app.get('credit_score', 'N/A')}  
**Monthly Income**: ₹{app.get('monthly_income', 0):,.0f}  
**Existing Loans**: {app.get('existing_loans', 'None')}  

**Action Required**: Review and approve/reject this application  
---
"""
        return app_list
        
    except Exception as e:
        return f"❌ Error loading applications: {e}"

def get_credit_analysis(app_id: str) -> str:
    """Get detailed credit analysis for a loan application"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please login first"
    
    if not loan_db or not credit_analyst:
        return "❌ Credit analysis system not available"
    
    if not app_id:
        return "❌ Please enter Application ID"
    
    try:
        applications = loan_db.get_applications_for_mfi(current_mfi_id)
        application = None
        
        for app in applications:
            if app['application_id'] == app_id:
                application = app
                break
        
        if not application:
            return f"❌ Application {app_id} not found"
        
        # Use CreditSense analyst to analyze the borrower profile
        borrower_profile = application['borrower_profile']
        
        # Generate comprehensive credit analysis
        analysis_result = credit_analyst.analyze_loan_application(
            borrower_data=borrower_profile,
            loan_amount=application['loan_amount'],
            loan_purpose=application['loan_purpose'],
            collateral=application.get('collateral', ''),
            credit_score=application.get('credit_score', 650)
        )
        
        return f"""
## 🎯 CreditSense Analysis Report

### Application Details
**Application ID**: {app_id}  
**Borrower**: {application['borrower_name']}  
**Requested Amount**: ₹{application['loan_amount']:,.0f}  
**Purpose**: {application['loan_purpose']}  

### Credit Assessment
{analysis_result.get('credit_assessment', 'Analysis not available')}

### Risk Factors
{analysis_result.get('risk_factors', 'Risk analysis not available')}

### Recommendation
{analysis_result.get('recommendation', 'No recommendation available')}

### Suggested Terms
{analysis_result.get('suggested_terms', 'No terms suggested')}
"""
        
    except Exception as e:
        return f"❌ Error generating credit analysis: {e}"

def approve_loan_application(app_id: str, approved_amount: float, loan_tenure: int, interest_rate: float, comments: str, disbursement_date: str) -> str:
    """Approve a loan application"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please login first"
    
    if not loan_db:
        return "❌ Loan system not available"
    
    if not app_id or approved_amount <= 0 or interest_rate <= 0 or loan_tenure <= 0:
        return "❌ Please fill all required fields with valid values"
    
    try:
        # Calculate EMI and total amount
        monthly_rate = interest_rate / 100 / 12
        emi_amount = approved_amount * monthly_rate * (1 + monthly_rate)**loan_tenure / ((1 + monthly_rate)**loan_tenure - 1)
        total_amount = emi_amount * loan_tenure
        
        # Prepare approval data
        approval_data = {
            'approved_amount': approved_amount,
            'loan_tenure': loan_tenure,
            'interest_rate': interest_rate,
            'emi_amount': round(emi_amount, 2),
            'total_amount': round(total_amount, 2),
            'comments': comments,
            'disbursement_date': disbursement_date or datetime.now().isoformat()
        }
        
        # Approve the loan
        success = loan_db.approve_loan(app_id, approval_data)
        
        if success:
            return f"""
✅ **Loan Application Approved Successfully!**

**Application ID**: {app_id}  
**Approved Amount**: ₹{approved_amount:,.0f}  
**Loan Tenure**: {loan_tenure} months  
**Interest Rate**: {interest_rate}% per annum  
**EMI Amount**: ₹{emi_amount:,.2f}  
**Total Payable**: ₹{total_amount:,.2f}  
**Disbursement Date**: {disbursement_date or 'Today'}  

**Next Steps:**
- Borrower will be notified of approval via SMS/WhatsApp
- EMI tracking has been automatically set up
- First EMI due 30 days from disbursement date
- Loan agreement will be generated for signatures

*The borrower can now track their loan and EMI payments through the borrower platform.*
"""
        else:
            return f"❌ Failed to approve application {app_id}"
            
    except Exception as e:
        return f"❌ Error approving loan: {e}"

def reject_loan_application(app_id: str, rejection_reason: str) -> str:
    """Reject a loan application"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please login first"
    
    if not loan_db:
        return "❌ Loan system not available"
    
    if not app_id or not rejection_reason:
        return "❌ Please provide Application ID and rejection reason"
    
    try:
        success = loan_db.reject_loan(app_id, rejection_reason)
        
        if success:
            return f"""
❌ **Loan Application Rejected**

**Application ID**: {app_id}  
**Reason**: {rejection_reason}  

The borrower will be notified of the rejection and the reason provided.
"""
        else:
            return f"❌ Failed to reject application {app_id}"
            
    except Exception as e:
        return f"❌ Error rejecting loan: {e}"

def view_active_portfolio() -> str:
    """View active loan portfolio for the MFI"""
    global current_mfi_id
    
    if not current_mfi_id:
        return "❌ Please login first"
    
    if not loan_db:
        return "❌ Loan system not available"
    
    try:
        # Get all EMI tracking data for this MFI
        all_loans = []
        for loan_id, loan_data in loan_db.emi_tracking.items():
            if loan_data['mfi_id'] == current_mfi_id:
                all_loans.append(loan_data)
        
        if not all_loans:
            return "ℹ️ No active loans in portfolio."
        
        # Calculate portfolio statistics
        total_principal = sum(loan['principal_amount'] for loan in all_loans)
        total_outstanding = sum(loan['outstanding_balance'] for loan in all_loans)
        active_loans = [loan for loan in all_loans if loan['status'] == 'active']
        completed_loans = [loan for loan in all_loans if loan['status'] == 'completed']
        
        portfolio_summary = f"""
## 💼 Loan Portfolio Summary

**Total Loans**: {len(all_loans)}  
**Active Loans**: {len(active_loans)}  
**Completed Loans**: {len(completed_loans)}  
**Total Principal Disbursed**: ₹{total_principal:,.0f}  
**Total Outstanding**: ₹{total_outstanding:,.0f}  
**Collection Rate**: {((total_principal - total_outstanding) / total_principal * 100) if total_principal > 0 else 0:.1f}%  

## 📊 Active Loans Details

"""
        
        for loan in active_loans:
            portfolio_summary += f"""
### 🔸 Loan ID: {loan['loan_id'][:12]}...
**Borrower**: {loan['borrower_id']}  
**Principal**: ₹{loan['principal_amount']:,.0f}  
**Outstanding**: ₹{loan['outstanding_balance']:,.0f}  
**EMI**: ₹{loan['emi_amount']:,.0f}  
**Next Due**: {loan.get('next_due_date', 'N/A')[:10]}  
**Payments Made**: {len(loan['payments'])}  
---
"""
        
        return portfolio_summary
        
    except Exception as e:
        return f"❌ Error loading portfolio: {e}"

def get_application_ids_list():
    """Get list of pending application IDs for dropdown - returns tuple for both dropdowns"""
    global current_mfi_id
    
    if not current_mfi_id or not loan_db:
        app_list = ["No applications available"]
        return gr.update(choices=app_list, value=app_list[0]), gr.update(choices=app_list, value=app_list[0])
    
    try:
        applications = loan_db.get_applications_for_mfi(current_mfi_id)
        pending_apps = [app for app in applications if app['status'] == 'pending']
        
        if not pending_apps:
            app_list = ["No pending applications"]
            return gr.update(choices=app_list, value=app_list[0]), gr.update(choices=app_list, value=app_list[0])
        
        app_list = [f"{app['application_id']} - {app['borrower_name']} - ₹{app['loan_amount']:,.0f}" 
                    for app in pending_apps]
        return gr.update(choices=app_list, value=None), gr.update(choices=app_list, value=None)
    except Exception as e:
        app_list = ["Error loading applications"]
        return gr.update(choices=app_list, value=app_list[0]), gr.update(choices=app_list, value=app_list[0])

def get_loan_details_from_dropdown(app_dropdown_value: str):
    """Extract loan details when application is selected from dropdown"""
    global current_mfi_id
    
    if not current_mfi_id or not loan_db:
        return 0, 12, ""  # default amount, tenure, purpose
    
    if not app_dropdown_value or app_dropdown_value in ["No applications", "No pending applications", "No applications available", "Error loading applications"]:
        return 0, 12, ""
    
    try:
        # Extract application ID from dropdown
        app_id = app_dropdown_value.split(' - ')[0]
        
        # Find the application
        applications = loan_db.get_applications_for_mfi(current_mfi_id)
        application = None
        
        for app in applications:
            if app['application_id'] == app_id and app['status'] == 'pending':
                application = app
                break
        
        if application:
            return (
                application['loan_amount'],  # requested amount
                application['loan_tenure'],  # requested tenure
                application['loan_purpose']  # loan purpose
            )
        else:
            return 0, 12, ""
            
    except Exception as e:
        return 0, 12, ""

# Define the Gradio interface
def create_mfi_interface():
    """Create the main MFI Gradio interface"""
    
    with gr.Blocks(title="MFI Platform - GramSetuAI", theme=gr.themes.Soft()) as mfi_app:
        
        # State management
        login_state = gr.State(False)
        
        gr.Markdown("""
        # 🏢 MFI Platform - GramSetuAI
        ### Microfinance Institution Management & Analytics System
        """)
        
        with gr.Tabs() as tabs:
            
            # Combined Authentication Tab
            with gr.Tab("🔐 Authentication", id="auth_tab"):
                
                # Login Section
                with gr.Column():
                    gr.Markdown("## 🔐 MFI Login")
                    gr.Markdown("*Select your MFI from the dropdown to access your dashboard:*")
                    
                    mfi_login_dropdown = gr.Dropdown(
                        label="Select Your MFI",
                        choices=get_available_mfis_for_login(),
                        value="Select an MFI"
                    )
                    
                    with gr.Row():
                        refresh_mfi_list_btn = gr.Button("🔄 Refresh MFI List", variant="secondary")
                        login_btn = gr.Button("🔑 Login to Dashboard", variant="primary")
                    
                    login_result = gr.Textbox(label="Login Status", interactive=False)
                    
                    gr.Markdown("---")
                    
                # Registration Section
                with gr.Column():
                    gr.Markdown("## 📝 Register New MFI")
                    gr.Markdown("*Don't have an account? Register your MFI below:*")
                    
                    with gr.Accordion("🏢 Basic Institution Details", open=True):
                        with gr.Row():
                            reg_mfi_name = gr.Textbox(label="MFI Name *", placeholder="e.g., Karnataka Rural Development Corporation")
                            reg_registration_number = gr.Textbox(label="Registration Number *", placeholder="e.g., NBFC-MFI-123456")
                        
                        with gr.Row():
                            reg_entity_type = gr.Dropdown(
                                label="Type of Entity",
                                choices=["NBFC-MFI", "NGO-MFI", "Cooperative", "SHG Federation", "Other"],
                                value="NBFC-MFI"
                            )
                            reg_year_establishment = gr.Number(label="Year of Establishment", value=2020, precision=0)
                        
                        reg_head_office = gr.Textbox(label="Head Office Address", placeholder="Complete address with city, state, pincode", lines=3)
                        reg_operating_states = gr.Textbox(label="Operating States/Regions", placeholder="e.g., Karnataka, Tamil Nadu, Andhra Pradesh")
                        
                        with gr.Row():
                            reg_contact_name = gr.Textbox(label="Contact Person Name", placeholder="Full name")
                            reg_contact_role = gr.Textbox(label="Contact Person Role", placeholder="e.g., CEO, General Manager")
                        
                        with gr.Row():
                            reg_contact_email = gr.Textbox(label="Email", placeholder="contact@mfi.org")
                            reg_contact_phone = gr.Textbox(label="Phone", placeholder="+91-XXXXXXXXXX")
                            reg_contact_whatsapp = gr.Textbox(label="WhatsApp", placeholder="+91-XXXXXXXXXX")
                    
                    with gr.Accordion("📊 Operational Metrics"):
                        with gr.Row():
                            reg_active_borrowers = gr.Number(label="Number of Active Borrowers", value=0, precision=0)
                            reg_portfolio_size = gr.Number(label="Loan Portfolio Size (₹)", value=0, precision=2)
                            reg_average_loan = gr.Number(label="Average Loan Size (₹)", value=0, precision=2)
                        
                        with gr.Row():
                            reg_min_loan = gr.Number(label="Minimum Loan Amount (₹)", value=5000, minimum=1000)
                            reg_max_loan = gr.Number(label="Maximum Loan Amount (₹)", value=100000, minimum=10000)
                        
                        reg_loan_products = gr.Textbox(label="Loan Products Offered", placeholder="e.g., Individual loans, Group loans, Agricultural loans", lines=2)
                        reg_repayment_freq = gr.Textbox(label="Repayment Frequencies", placeholder="e.g., Weekly, Monthly, Bi-weekly")
                    
                    with gr.Accordion("👥 Team & Staff Info"):
                        with gr.Row():
                            reg_field_officers = gr.Number(label="Total Field Officers", value=0, precision=0)
                            reg_branches = gr.Number(label="Branches/Field Centers", value=0, precision=0)
                        
                        reg_ops_contacts = gr.Textbox(label="Ops Manager Contacts", placeholder="Names and contact details", lines=2)
                        reg_training = gr.Textbox(label="Training & Onboarding Process", placeholder="Brief description of staff training", lines=2)
                    
                    with gr.Accordion("💻 Technology Usage"):
                        reg_loan_software = gr.Textbox(label="Core Loan Management Software", placeholder="e.g., Mifos, Custom Excel, Other software")
                        reg_digital_tools = gr.Textbox(label="Digital Lending Tools/Apps", placeholder="Mobile apps, web platforms used")
                        
                        with gr.Row():
                            reg_data_format = gr.Dropdown(
                                label="Preferred Data Format",
                                choices=["CSV", "Excel", "Google Sheets", "Database", "API"],
                                value="Excel"
                            )
                            reg_integration = gr.Textbox(label="Integration Preferences", placeholder="e.g., Webhook, N8N, API, Manual")
                    
                    with gr.Accordion("💰 Financial & Compliance"):
                        reg_funding_sources = gr.Textbox(label="Funding Sources", placeholder="e.g., NABARD, SIDBI, Banks, Donors", lines=2)
                        reg_interest_rates = gr.Textbox(label="Interest Rates Charged", placeholder="e.g., 18-24% per annum")
                        
                        with gr.Row():
                            reg_par = gr.Number(label="Portfolio at Risk (PAR) > 30 Days %", value=0, precision=2)
                            reg_credit_bureau = gr.Dropdown(label="Credit Bureau Integration", choices=["Yes", "No"], value="No")
                        
                        reg_audit_date = gr.Textbox(label="Latest Audit Done On", placeholder="e.g., March 2024")
                    
                    with gr.Accordion("🎯 Target Segments"):
                        reg_borrower_focus = gr.Textbox(label="Borrower Type Focus", placeholder="e.g., SHGs, Individual women, Entrepreneurs", lines=2)
                        reg_sector_focus = gr.Textbox(label="Primary Sector Focus", placeholder="e.g., Agriculture, Trade, Livestock, Services", lines=2)
                        reg_tenure_range = gr.Textbox(label="Preferred Loan Tenure Range", placeholder="e.g., 6-24 months")
                        reg_geographies = gr.Textbox(label="Geographies Covered", placeholder="Villages, districts, blocks covered", lines=2)
                    
                    with gr.Accordion("🎯 Goals & Challenges"):
                        reg_challenges = gr.Textbox(label="Top 3 Challenges", placeholder="e.g., Loan defaults, Manual operations, Data management", lines=3)
                        reg_vision = gr.Textbox(label="Vision for Next 2 Years", placeholder="Scale, digitization, expansion plans", lines=3)
                        reg_support = gr.Textbox(label="Need Support In", placeholder="e.g., Credit Scoring, Risk Forecasting, Operations", lines=2)
                    
                    with gr.Accordion("🔐 Create Login Credentials"):
                        with gr.Row():
                            reg_username = gr.Textbox(label="Username *", placeholder="Choose a unique username")
                            reg_password = gr.Textbox(label="Password *", type="password", placeholder="Create a strong password")
                    
                    register_btn = gr.Button("🏢 Register MFI", variant="primary", size="lg")
                    register_result = gr.Textbox(label="Registration Status", interactive=False)
            
            # Dashboard Tab
            with gr.Tab("📊 Dashboard", id="dashboard_tab"):
                dashboard_content = gr.Markdown("## Please log in to view your dashboard")
                
                with gr.Row():
                    refresh_dashboard_btn = gr.Button("🔄 Refresh Dashboard", variant="secondary")
                    logout_btn = gr.Button("🚪 Logout", variant="outline")
                
                logout_result = gr.Textbox(label="Logout Status", interactive=False, visible=False)
            
            # Loan Management Tab
            with gr.Tab("📋 Loan Management", id="loan_management_tab"):
                gr.Markdown("## 📋 Loan Application Management")
                
                with gr.Tabs():
                    with gr.Tab("📄 Pending Applications"):
                        gr.Markdown("### Review Loan Applications")
                        
                        refresh_applications_btn = gr.Button("🔄 Refresh Applications", variant="secondary")
                        applications_display = gr.Markdown()
                        
                        gr.Markdown("### Quick Actions")
                        with gr.Row():
                            app_id_input = gr.Textbox(label="Application ID", placeholder="Enter application ID")
                            get_analysis_btn = gr.Button("🎯 Get Credit Analysis", variant="primary")
                        
                        credit_analysis_display = gr.Markdown()
                    
                    with gr.Tab("✅ Approve Loan"):
                        gr.Markdown("### Approve Loan Application")
                        gr.Markdown("*Select an application below to auto-fill details. You can modify the loan terms as needed.*")
                        
                        with gr.Row():
                            approve_app_dropdown = gr.Dropdown(label="Select Application", choices=["No applications"])
                            loan_purpose_display = gr.Textbox(label="Loan Purpose", interactive=False)
                        
                        with gr.Row():
                            approved_amount_input = gr.Number(label="Approved Amount (₹)", minimum=1000, maximum=1000000)
                            loan_tenure_input = gr.Number(label="Loan Tenure (Months)", minimum=3, maximum=60, value=12, precision=0)
                        
                        with gr.Row():
                            interest_rate_input = gr.Number(label="Interest Rate (% per annum)", minimum=1, maximum=50, value=12)
                            disbursement_date_input = gr.Textbox(label="Disbursement Date (Optional)", placeholder="YYYY-MM-DD")
                        
                        approval_comments_input = gr.Textbox(label="Approval Comments", placeholder="Additional terms or conditions", lines=2)
                        approve_btn = gr.Button("✅ Approve Loan", variant="primary")
                        approval_result = gr.Markdown()
                    
                    with gr.Tab("❌ Reject Application"):
                        gr.Markdown("### Reject Loan Application")
                        
                        with gr.Row():
                            reject_app_dropdown = gr.Dropdown(label="Select Application", choices=["No applications"])
                            rejection_reason_input = gr.Textbox(label="Rejection Reason", placeholder="Explain why the application is being rejected")
                        
                        reject_btn = gr.Button("❌ Reject Application", variant="secondary")
                        rejection_result = gr.Markdown()
                    
                    with gr.Tab("💼 Portfolio Overview"):
                        gr.Markdown("### Active Loan Portfolio")
                        
                        refresh_portfolio_btn = gr.Button("🔄 Refresh Portfolio", variant="secondary")
                        portfolio_display = gr.Markdown()
            
            # Analytics Tab
            with gr.Tab("📈 Analytics", id="analytics_tab"):
                gr.Markdown("## 🧠 AI-Powered Analytics")
                
                with gr.Tabs():
                    # FundFlow Forecaster Tab
                    with gr.Tab("💰 FundFlow Forecaster"):
                        gr.Markdown("### Portfolio Health & Cashflow Forecasting")
                        
                        with gr.Row():
                            ff_regional_filter = gr.Textbox(label="Regional Filter", placeholder="Optional: e.g., Karnataka")
                            ff_months_ahead = gr.Slider(label="Forecast Months", minimum=1, maximum=12, value=6, step=1)
                        
                        ff_forecast_btn = gr.Button("💰 Generate Cashflow Forecast", variant="primary")
                        ff_result = gr.Markdown("## Click 'Generate Cashflow Forecast' to see portfolio health analysis and cash flow projections")
                    
                    # PolicyPulse Advisor Tab
                    with gr.Tab("📋 PolicyPulse Advisor"):
                        gr.Markdown("### Compliance & Government Scheme Updates")
                        
                        with gr.Row():
                            pp_state = gr.Textbox(label="State Filter", placeholder="Optional: e.g., Karnataka")
                            pp_borrower_occupation = gr.Dropdown(
                                label="Borrower Occupation Filter",
                                choices=["", "Agriculture", "Small Business", "Trade", "Services"],
                                value=""
                            )
                        
                        pp_scan_btn = gr.Button("📋 Scan Policy Updates", variant="primary")
                        pp_result = gr.Markdown("## Click 'Scan Policy Updates' to see compliance updates and government scheme opportunities")
                    
                    # AI Chat Assistant for MFI Operations
                    with gr.Tab("💬 AI Financial Assistant"):
                        gr.Markdown("### 🤖 Expert Financial Assistant for MFI Operations")
                        gr.Markdown("*Get expert guidance on portfolio management, regulatory compliance, risk assessment, and operational efficiency*")
                        
                        # Chat interface
                        with gr.Row():
                            with gr.Column(scale=3):
                                mfi_chatbot = gr.Chatbot(
                                    label="MFI Operations Assistant", 
                                    height=400,
                                    show_label=True,
                                    bubble_full_width=False
                                )
                                
                                with gr.Row():
                                    mfi_msg = gr.Textbox(
                                        label="Your Question",
                                        placeholder="Ask about portfolio management, compliance, risk assessment, lending best practices...",
                                        lines=2,
                                        scale=4
                                    )
                                    mfi_send_btn = gr.Button("Send", variant="primary", scale=1)
                                
                                mfi_clear_btn = gr.Button("Clear Chat", variant="secondary")
                            
                            with gr.Column(scale=1):
                                gr.Markdown("### 💡 Expert Topics")
                                mfi_suggested_display = gr.Markdown()
                        
                        # MFI Chat functions
                        def get_mfi_rag_response(message: str) -> str:
                            """Get response from RAG system for MFI users"""
                            if not rag_system:
                                return "🏦 **MFI Operations Assistant**\n\nI'm currently being set up to help you with MFI operations. In the meantime, here's some general guidance:\n\n• **Monitor PAR rates** regularly to maintain portfolio health\n• **Diversify your portfolio** across different borrower segments\n• **Ensure regulatory compliance** with RBI guidelines\n• **Use technology** to streamline operations and reduce costs\n• **Focus on borrower education** to improve repayment rates\n\nPlease try again in a few moments!"
                            
                            try:
                                response = rag_system.get_response(message, user_type="lender")
                                return f"🏦 **MFI Operations Assistant**\n\n{response}"
                            except Exception as e:
                                return f"🏦 **MFI Operations Assistant**\n\nI'm experiencing technical difficulties. Please try again.\n\n**Topics I can help with:**\n• Portfolio risk management\n• Regulatory compliance\n• Lending best practices\n• Technology solutions\n• Borrower assessment\n\nError: {str(e)}"
                        
                        def respond_to_mfi_query(message, history):
                            if not message.strip():
                                return history, ""
                            
                            response = get_mfi_rag_response(message)
                            history = history or []
                            history.append([message, response])
                            return history, ""
                        
                        def clear_mfi_chat():
                            if rag_system:
                                try:
                                    rag_system.clear_chat_history()
                                except:
                                    pass
                            return []
                        
                        def load_mfi_suggestions():
                            if rag_system:
                                try:
                                    questions = rag_system.get_suggested_questions("lender")
                                except:
                                    questions = [
                                        "How do I assess borrower creditworthiness?",
                                        "What are the current RBI guidelines?",
                                        "How do I manage portfolio risk?",
                                        "What are best practices for collections?",
                                        "How do I calculate appropriate interest rates?",
                                        "What technology solutions can help?"
                                    ]
                            else:
                                questions = [
                                    "How do I assess borrower creditworthiness?",
                                    "What are the current RBI guidelines?",
                                    "How do I manage portfolio risk?",
                                    "What are best practices for collections?"
                                ]
                            
                            formatted = "\n".join([f"• {q}" for q in questions[:6]])
                            return f"""**Click on any topic:**

{formatted}

**Or ask your own question!**"""
        
        # Event handlers
        def handle_login(mfi_selection):
            message, success = login_mfi(mfi_selection)
            if success:
                dashboard = get_mfi_dashboard()
                # Also get application list for dropdowns
                approve_update, reject_update = get_application_ids_list()
                return message, success, dashboard, approve_update, reject_update
            return message, success, "## Please log in to view your dashboard", gr.update(choices=["No applications"], value="No applications"), gr.update(choices=["No applications"], value="No applications")
        
        def refresh_mfi_list():
            """Refresh the MFI dropdown list"""
            return gr.update(choices=get_available_mfis_for_login(), value="Select an MFI")
        
        def handle_logout():
            message, success = logout_mfi()
            return message, not success, "## Please log in to view your dashboard"
        
        def refresh_dashboard():
            if current_mfi_profile:
                return get_mfi_dashboard()
            return "## Please log in to view your dashboard"
        
        # Wire up the events
        login_btn.click(
            handle_login,
            inputs=[mfi_login_dropdown],
            outputs=[login_result, login_state, dashboard_content, approve_app_dropdown, reject_app_dropdown]
        )
        
        refresh_mfi_list_btn.click(
            refresh_mfi_list,
            outputs=[mfi_login_dropdown]
        )
        
        register_btn.click(
            register_new_mfi,
            inputs=[
                reg_mfi_name, reg_registration_number, reg_entity_type, reg_year_establishment,
                reg_head_office, reg_operating_states, reg_contact_name, reg_contact_role,
                reg_contact_email, reg_contact_phone, reg_contact_whatsapp,
                reg_active_borrowers, reg_portfolio_size, reg_average_loan, reg_min_loan, reg_max_loan, reg_loan_products, reg_repayment_freq,
                reg_field_officers, reg_branches, reg_ops_contacts, reg_training,
                reg_loan_software, reg_digital_tools, reg_data_format, reg_integration,
                reg_funding_sources, reg_interest_rates, reg_par, reg_credit_bureau, reg_audit_date,
                reg_borrower_focus, reg_sector_focus, reg_tenure_range, reg_geographies,
                reg_challenges, reg_vision, reg_support,
                reg_username, reg_password
            ],
            outputs=register_result
        )
        
        logout_btn.click(
            handle_logout,
            outputs=[logout_result, login_state, dashboard_content]
        )
        
        refresh_dashboard_btn.click(
            refresh_dashboard,
            outputs=dashboard_content
        )
        
        # Analytics event handlers - CreditSense removed (available in Loan Management)
        ff_forecast_btn.click(
            run_fundflow_forecast,
            inputs=[ff_regional_filter, ff_months_ahead],
            outputs=ff_result
        )
        
        pp_scan_btn.click(
            run_policy_pulse_scan,
            inputs=[pp_state, pp_borrower_occupation],
            outputs=pp_result
        )
        
        # MFI Chat Event Handlers
        mfi_send_btn.click(
            fn=respond_to_mfi_query,
            inputs=[mfi_msg, mfi_chatbot],
            outputs=[mfi_chatbot, mfi_msg]
        )
        
        mfi_msg.submit(
            fn=respond_to_mfi_query,
            inputs=[mfi_msg, mfi_chatbot],
            outputs=[mfi_chatbot, mfi_msg]
        )
        
        mfi_clear_btn.click(
            fn=clear_mfi_chat,
            outputs=[mfi_chatbot]
        )
        
        # Load MFI suggestions on startup
        app.load(
            fn=load_mfi_suggestions,
            outputs=[mfi_suggested_display]
        )
        
        # Loan management event handlers
        refresh_applications_btn.click(
            fn=view_pending_applications,
            outputs=[applications_display]
        ).then(
            fn=get_application_ids_list,
            outputs=[approve_app_dropdown, reject_app_dropdown]
        )
        
        get_analysis_btn.click(
            fn=get_credit_analysis,
            inputs=[app_id_input],
            outputs=[credit_analysis_display]
        )
        
        # Auto-fill loan details when application is selected
        approve_app_dropdown.change(
            fn=get_loan_details_from_dropdown,
            inputs=[approve_app_dropdown],
            outputs=[approved_amount_input, loan_tenure_input, loan_purpose_display]
        )
        
        # Also update reject dropdown when approve dropdown changes
        approve_app_dropdown.change(
            fn=lambda x: x,  # Just pass through the value
            inputs=[approve_app_dropdown],
            outputs=[reject_app_dropdown]
        )
        
        approve_btn.click(
            fn=lambda app_dropdown, amount, tenure, rate, comments, date: approve_loan_application(
                app_dropdown.split(' - ')[0] if app_dropdown and app_dropdown not in ["No applications", "No pending applications", "No applications available", "Error loading applications"] else "",
                amount or 0, int(tenure or 12), rate or 0, comments or "", date or ""
            ),
            inputs=[approve_app_dropdown, approved_amount_input, loan_tenure_input, interest_rate_input, 
                   approval_comments_input, disbursement_date_input],
            outputs=[approval_result]
        ).then(
            # Refresh dropdowns after approval
            fn=get_application_ids_list,
            outputs=[approve_app_dropdown, reject_app_dropdown]
        )
        
        reject_btn.click(
            fn=lambda app_dropdown, reason: reject_loan_application(
                app_dropdown.split(' - ')[0] if app_dropdown and app_dropdown not in ["No applications", "No pending applications", "No applications available", "Error loading applications"] else "",
                reason or ""
            ),
            inputs=[reject_app_dropdown, rejection_reason_input],
            outputs=[rejection_result]
        ).then(
            # Refresh dropdowns after rejection
            fn=get_application_ids_list,
            outputs=[approve_app_dropdown, reject_app_dropdown]
        )
        
        refresh_portfolio_btn.click(
            fn=view_active_portfolio,
            outputs=[portfolio_display]
        )
    
    return mfi_app

if __name__ == "__main__":
    app = create_mfi_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        debug=True
    )
