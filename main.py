"""
Main CLI interface for Microfinance Agents
Test and interact with all agents from command line
"""

import os
import json
import sys
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.user_onboarding_agent import UserOnboardingAgent
from agents.document_processing_agent import DocumentProcessingAgent
from agents.property_verification_agent import PropertyVerificationAgent
from agents.voice_assistant_agent import VoiceAssistantAgent
from agents.credit_metrics_explainer import CreditMetricsExplainer
from agents.loan_risk_advisor_agent import LoanRiskAdvisorAgent

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_json_pretty(data: Dict[str, Any], max_length: int = 1000):
    """Print JSON data in a readable format"""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    if len(json_str) > max_length:
        json_str = json_str[:max_length] + "\n... (truncated)"
    print(json_str)

def test_user_onboarding():
    """Test User Onboarding Agent"""
    print_header("TESTING USER ONBOARDING AGENT")
    
    agent = UserOnboardingAgent()
    
    # Test with sample user inputs
    test_inputs = [
        "Hi, my name is Ramesh Kumar, I am 35 years old farmer from Davangere village. I have 2 acres of land and earn about 15000 rupees per month.",
        "नमस्ते, मेरा नाम सुनीता देवी है। मैं 28 साल की हूं और तिलकी गांव से हूं। मैं बुनाई का काम करती हूं।",
        "I have a bank account in Karnataka Bank and I am part of women's self help group. I save around 1000 rupees every month."
    ]
    
    user_data = {}
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n--- Test Input {i} ---")
        print(f"User says: {user_input}")
        
        # Extract information
        extracted = agent.extract_user_info(user_input, "english", user_data)
        user_data = extracted
        
        print("\nExtracted Information:")
        print_json_pretty(extracted, 500)
        
        # Get completeness validation
        validation = agent.validate_completeness(user_data)
        print(f"\nCompleteness Score: {validation['completeness_score']}%")
        print(f"Is Complete: {validation['is_complete']}")
        
        if not validation['is_complete']:
            questions = agent.ask_clarifying_questions(user_data, "english")
            print(f"\nClarifying Questions: {questions}")
    
    return user_data

def test_document_processing():
    """Test Document Processing Agent"""
    print_header("TESTING DOCUMENT PROCESSING AGENT")
    
    agent = DocumentProcessingAgent()
    
    # Simulate document processing
    sample_docs = [
        "data/sample_inputs/aadhaar_sample.jpg",
        "data/sample_inputs/bank_statement.pdf",
        "data/sample_inputs/property_doc.jpg"
    ]
    
    for doc_path in sample_docs:
        print(f"\n--- Processing Document: {doc_path} ---")
        
        # Detect document type
        detection = agent.detect_document_type(doc_path)
        print("Document Detection:")
        print_json_pretty(detection)
        
        if detection["is_valid_document"]:
            # Extract fields
            extraction = agent.extract_document_fields(
                doc_path, 
                detection["document_type"]
            )
            print("\nField Extraction:")
            print_json_pretty(extraction, 500)
            
            # Verify authenticity
            verification = agent.verify_document_authenticity(
                extraction,
                detection["document_type"]
            )
            print("\nVerification Results:")
            print_json_pretty(verification)

def test_property_verification():
    """Test Property Verification Agent"""
    print_header("TESTING PROPERTY VERIFICATION AGENT")
    
    agent = PropertyVerificationAgent()
    
    # Sample property document text
    sample_doc_text = """
    KARNATAKA GOVERNMENT
    REVENUE RECORD
    Survey No: 123/2A
    Village: Davangere
    Taluk: Davangere
    District: Davangere
    Owner: Ramesh Kumar S/O Suresh Kumar
    Area: 2 Acres 15 Guntas
    Classification: Dry Land
    Assessment: Rs. 2500 per year
    Registration Date: 15/03/2015
    """
    
    print("Sample Property Document:")
    print(sample_doc_text)
    
    # Parse property document
    parsed_data = agent.parse_property_document(sample_doc_text)
    print("\nParsed Property Data:")
    print_json_pretty(parsed_data, 800)
    
    # Calculate property value
    valuation = agent.calculate_property_value(parsed_data)
    print("\nProperty Valuation:")
    print_json_pretty(valuation, 600)

def test_voice_assistant():
    """Test Voice Assistant Agent"""
    print_header("TESTING VOICE ASSISTANT AGENT")
    
    agent = VoiceAssistantAgent()
    
    # Test voice queries (simulated)
    test_queries = [
        "What documents do I need for a loan application?",
        "How much interest rate for agriculture loan?",
        "Can I apply for loan without collateral?",
        "What is the maximum loan amount for farming?",
        "How long does loan approval take?"
    ]
    
    for query in test_queries:
        print(f"\n--- Query: {query} ---")
        
        # Simulate voice interaction
        result = agent.simulate_voice_interaction(query, "english")
        
        if result["success"]:
            print(f"Response: {result['llm_response']['response_text']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    
    # Show conversation history
    history = agent.get_conversation_history()
    print(f"\nConversation History: {len(history)} entries")

def test_credit_metrics():
    """Test Credit Metrics Explainer"""
    print_header("TESTING CREDIT METRICS EXPLAINER")
    
    explainer = CreditMetricsExplainer()
    
    # Sample user data for credit scoring
    sample_user = {
        "personal_info": {
            "full_name": "Ramesh Kumar",
            "age": "35"
        },
        "occupation_income": {
            "primary_occupation": "farmer",
            "monthly_income": "15000",
            "monthly_expenses": "12000",
            "seasonal_variation": "yes"
        },
        "financial_details": {
            "bank_account_status": "yes",
            "existing_loans": "small agriculture loan",
            "repayment_history": "good",
            "savings_per_month": "2000",
            "group_membership": "yes"
        },
        "land_property": {
            "owns_land": "yes",
            "land_area": "2 acres"
        },
        "household_location": {
            "house_type": "semi-pucca",
            "district": "Davangere"
        },
        "digital_literacy": {
            "owns_smartphone": "yes"
        }
    }
    
    print("Sample User Data:")
    print_json_pretty(sample_user, 500)
    
    # Generate credit report
    credit_report = explainer.generate_credit_report(sample_user, "english")
    
    print(f"\nCredit Score: {credit_report['credit_score_calculation']['total_score']}")
    print(f"Score Range: {credit_report['credit_score_calculation']['score_range']}")
    print(f"Peer Percentile: {credit_report['peer_comparison']['user_percentile']}")
    
    print("\nCredit Explanation (first 300 chars):")
    explanation = credit_report['explanation']
    print(explanation[:300] + "..." if len(explanation) > 300 else explanation)
    
    return credit_report

def test_loan_risk_advisor():
    """Test Loan Risk Advisor Agent"""
    print_header("TESTING LOAN RISK ADVISOR AGENT")
    
    advisor = LoanRiskAdvisorAgent()
    
    # Sample user data
    sample_user = {
        "personal_info": {"full_name": "Ramesh Kumar", "phone_number": "9876543210"},
        "occupation_income": {
            "primary_occupation": "farmer",
            "monthly_income": "15000",
            "monthly_expenses": "10000",
            "seasonal_variation": "yes"
        },
        "financial_details": {
            "bank_account_status": "yes",
            "existing_loans": "small agriculture loan",
            "repayment_history": "good",
            "group_membership": "yes"
        },
        "land_property": {"owns_land": "yes", "land_area": "2 acres"},
        "household_location": {"house_type": "semi-pucca"}
    }
    
    # Sample loan requests
    loan_requests = [
        {"amount": 50000, "type": "agriculture", "purpose": "crop cultivation"},
        {"amount": 30000, "type": "micro_business", "purpose": "shop expansion"},
        {"amount": 100000, "type": "housing", "purpose": "house repair"}
    ]
    
    for loan_request in loan_requests:
        print(f"\n--- Loan Request: {loan_request} ---")
        
        # Assess risk
        risk_assessment = advisor.assess_loan_risk(sample_user, loan_request)
        print(f"Risk Score: {risk_assessment['overall_risk_score']}")
        print(f"Risk Category: {risk_assessment['risk_category']}")
        print(f"Recommendation: {risk_assessment['approval_recommendation']}")
        
        # Get loan terms
        loan_terms = advisor.recommend_loan_terms(risk_assessment)
        print(f"Recommended Amount: ₹{loan_terms['recommended_amount']:,.0f}")
        print(f"Interest Rate: {loan_terms['interest_rate']}%")
        print(f"Monthly EMI: ₹{loan_terms['monthly_emi']:,.0f}")
        print(f"Tenure: {loan_terms['tenure_months']} months")

def run_complete_workflow():
    """Run complete workflow integrating all agents"""
    print_header("COMPLETE MICROFINANCE WORKFLOW")
    
    print("🚀 Starting complete microfinance assessment workflow...")
    
    # Step 1: User Onboarding
    print("\n📝 Step 1: User Onboarding")
    user_data = test_user_onboarding()
    
    # Step 2: Credit Scoring
    print("\n📊 Step 2: Credit Assessment")
    explainer = CreditMetricsExplainer()
    credit_report = explainer.generate_credit_report(user_data, "english")
    
    # Step 3: Loan Risk Analysis
    print("\n🎯 Step 3: Loan Risk Analysis")
    advisor = LoanRiskAdvisorAgent()
    loan_request = {"amount": 50000, "type": "agriculture", "purpose": "crop cultivation"}
    
    risk_assessment = advisor.assess_loan_risk(user_data, loan_request)
    loan_terms = advisor.recommend_loan_terms(risk_assessment)
    
    # Final Summary
    print_header("WORKFLOW SUMMARY")
    print(f"Applicant: {user_data.get('personal_info', {}).get('full_name', 'Unknown')}")
    print(f"Credit Score: {credit_report['credit_score_calculation']['total_score']}")
    print(f"Risk Category: {risk_assessment['risk_category']}")
    print(f"Loan Amount Requested: ₹{loan_request['amount']:,}")
    print(f"Recommended Amount: ₹{loan_terms['recommended_amount']:,.0f}")
    print(f"Interest Rate: {loan_terms['interest_rate']}%")
    print(f"Monthly EMI: ₹{loan_terms['monthly_emi']:,.0f}")
    print(f"Final Recommendation: {risk_assessment['approval_recommendation']}")

def main():
    """Main CLI interface"""
    print_header("MICROFINANCE AGENTS - TESTING SUITE")
    print("Choose an option to test:")
    print("1. User Onboarding Agent")
    print("2. Document Processing Agent")
    print("3. Property Verification Agent")
    print("4. Voice Assistant Agent")
    print("5. Credit Metrics Explainer")
    print("6. Loan Risk Advisor Agent")
    print("7. Run Complete Workflow")
    print("8. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                test_user_onboarding()
            elif choice == "2":
                test_document_processing()
            elif choice == "3":
                test_property_verification()
            elif choice == "4":
                test_voice_assistant()
            elif choice == "5":
                test_credit_metrics()
            elif choice == "6":
                test_loan_risk_advisor()
            elif choice == "7":
                run_complete_workflow()
            elif choice == "8":
                print("Goodbye! 👋")
                break
            else:
                print("Invalid choice. Please enter 1-8.")
                
        except KeyboardInterrupt:
            print("\n\nExiting... Goodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
