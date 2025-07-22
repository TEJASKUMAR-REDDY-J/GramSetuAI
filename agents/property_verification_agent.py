"""
Property Verification Agent
Parses land/property record fields and validates ownership
Supports Karnataka land records format
"""

import os
import json
from groq import Groq
from typing import Dict, Any, Optional, List
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import get_language_prompt, generate_cache_key
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PropertyVerificationAgent:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("GROQ API key is required. Set GROQ_API_KEY environment variable or pass groq_api_key parameter.")
        self.client = Groq(api_key=self.groq_api_key)
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.cache = {}
        
        # Karnataka specific property document types
        self.property_document_types = [
            "patta_document",
            "katha_certificate", 
            "revenue_record",
            "survey_settlement",
            "mutation_record",
            "title_deed",
            "sale_deed",
            "gift_deed"
        ]
        
        # Land classification types in Karnataka
        self.land_classifications = [
            "Dry",
            "Wet", 
            "Garden",
            "Kumki",
            "Sarkar",
            "Inam",
            "Government"
        ]
    
    def parse_property_document(self, document_text: str, document_type: str = "auto", language: str = "english") -> Dict[str, Any]:
        """
        Parse property document text and extract key fields
        
        Args:
            document_text (str): Raw text from property document
            document_type (str): Type of property document or 'auto' for detection
            language (str): Target language for response
            
        Returns:
            Dict: Parsed property information
        """
        
        # Check cache
        cache_key = generate_cache_key({"text": document_text, "type": document_type})
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        system_prompt = get_language_prompt(language, "document_system")
        
        parsing_prompt = f"""
{system_prompt}

Parse this Karnataka property document and extract all relevant fields. Return as structured JSON.

Document Text: {document_text}

Extract the following information:
{{
    "document_analysis": {{
        "document_type": "detected type from: {', '.join(self.property_document_types)}",
        "language_detected": "english/kannada/hindi",
        "confidence": "high/medium/low",
        "completeness": "complete/partial/incomplete"
    }},
    "property_details": {{
        "survey_number": "",
        "sub_division": "",
        "village": "",
        "taluk": "", 
        "district": "",
        "total_area": "",
        "area_unit": "acres/guntas/cents",
        "land_classification": "from: {', '.join(self.land_classifications)}",
        "land_type": "irrigated/dry/garden/other",
        "boundaries": {{
            "north": "",
            "south": "",
            "east": "",
            "west": ""
        }}
    }},
    "ownership_details": {{
        "owner_name": "",
        "father_name": "",
        "ownership_type": "sole/joint/inheritance",
        "share_details": "",
        "acquisition_date": "",
        "acquisition_mode": "purchase/inheritance/gift/allotment"
    }},
    "revenue_details": {{
        "revenue_village": "",
        "revenue_survey_number": "",
        "assessment_number": "",
        "annual_assessment": "",
        "water_rate": "",
        "total_assessment": ""
    }},
    "verification_fields": {{
        "registration_date": "",
        "registration_number": "",
        "sub_registrar_office": "",
        "stamp_duty_paid": "",
        "registration_fee_paid": ""
    }},
    "encumbrances": {{
        "mortgages": [],
        "loans_against_property": [],
        "legal_disputes": [],
        "government_dues": ""
    }}
}}

Parse the document and return ONLY the JSON:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": parsing_prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                
            parsed_data = json.loads(result_text)
            
            # Cache result
            self.cache[cache_key] = parsed_data
            
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing property document: {e}")
            return self._get_empty_property_template()
    
    def verify_property_ownership(self, property_data: Dict[str, Any], user_data: Dict[str, Any], language: str = "english") -> Dict[str, Any]:
        """
        Verify property ownership against user profile
        
        Args:
            property_data (Dict): Parsed property information
            user_data (Dict): User profile data
            language (str): Target language for response
            
        Returns:
            Dict: Ownership verification results
        """
        
        system_prompt = get_language_prompt(language, "document_system")
        
        verification_prompt = f"""
{system_prompt}

Verify property ownership by cross-matching property document data with user profile.

Property Data: {json.dumps(property_data, indent=2)}

User Profile: {json.dumps(user_data, indent=2)}

Verify and return JSON:
{{
    "ownership_verification": {{
        "name_match": "exact/partial/no_match",
        "name_variations_found": [],
        "father_name_match": "exact/partial/no_match", 
        "address_consistency": "consistent/inconsistent/insufficient_data",
        "verification_status": "verified/needs_verification/rejected"
    }},
    "property_valuation": {{
        "estimated_market_value": "",
        "assessment_basis": "location/area/land_type",
        "collateral_viability": "high/medium/low",
        "marketability": "high/medium/low"
    }},
    "risk_factors": {{
        "legal_disputes": "none/minor/major",
        "encumbrances": "clear/minor_liens/major_liens",
        "title_clarity": "clear/unclear/disputed",
        "location_risk": "low/medium/high"
    }},
    "recommendations": {{
        "loan_eligibility": "eligible/conditional/not_eligible",
        "collateral_percentage": "percentage of property value eligible as collateral",
        "additional_verification_needed": [],
        "risk_mitigation": []
    }},
    "confidence_score": "0-100"
}}

Analyze and return ONLY the JSON:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": verification_prompt}
                ],
                max_tokens=1200,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Error verifying property ownership: {e}")
            return {
                "ownership_verification": {
                    "verification_status": "error",
                    "error_message": str(e)
                },
                "confidence_score": "0"
            }
    
    def calculate_property_value(self, property_data: Dict[str, Any], market_rates: Dict[str, float] = None, language: str = "english") -> Dict[str, Any]:
        """
        Calculate estimated property value based on location and land type
        
        Args:
            property_data (Dict): Property details
            market_rates (Dict): Optional market rates per unit
            language (str): Target language for response
            
        Returns:
            Dict: Property valuation details
        """
        
        if not market_rates:
            # Default market rates for Karnataka (per acre in INR)
            market_rates = {
                "Dry": 200000,
                "Wet": 500000,
                "Garden": 300000,
                "Kumki": 150000,
                "urban": 1000000,
                "semi_urban": 400000,
                "rural": 200000
            }
        
        system_prompt = get_language_prompt(language, "document_system")
        
        valuation_prompt = f"""
{system_prompt}

Calculate property value based on the given property details and market rates.

Property Details: {json.dumps(property_data, indent=2)}

Market Rates (per acre): {json.dumps(market_rates, indent=2)}

Calculate and return JSON:
{{
    "property_valuation": {{
        "base_rate_per_unit": "",
        "total_area_in_acres": "",
        "location_factor": "multiplier based on location (0.5 to 2.0)",
        "land_type_factor": "multiplier based on land classification",
        "calculated_value": "",
        "market_value_range": {{
            "minimum": "",
            "maximum": "",
            "most_likely": ""
        }}
    }},
    "valuation_factors": {{
        "positive_factors": [],
        "negative_factors": [],
        "location_advantages": [],
        "infrastructure_access": []
    }},
    "loan_collateral_assessment": {{
        "eligible_collateral_value": "typically 60-80% of market value",
        "loan_to_value_ratio": "recommended LTV ratio",
        "collateral_grade": "A/B/C grade",
        "risk_category": "low/medium/high"
    }},
    "validation_notes": "explanation of valuation methodology"
}}

Calculate valuation and return ONLY the JSON:
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": valuation_prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            if result_text.startswith('```json'):
                result_text = result_text.split('```json')[1].split('```')[0]
            elif result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Error calculating property value: {e}")
            return {
                "property_valuation": {
                    "calculated_value": "Error in calculation",
                    "error": str(e)
                }
            }
    
    def generate_property_report(self, property_data: Dict[str, Any], verification_result: Dict[str, Any], valuation_result: Dict[str, Any], language: str = "english") -> str:
        """
        Generate comprehensive property verification report
        
        Args:
            property_data (Dict): Parsed property data
            verification_result (Dict): Ownership verification results
            valuation_result (Dict): Property valuation results
            language (str): Target language for response
            
        Returns:
            str: Formatted property report
        """
        
        system_prompt = get_language_prompt(language, "document_system")
        
        report_prompt = f"""
{system_prompt}

Generate a comprehensive property verification report for microfinance loan assessment.

Property Data: {json.dumps(property_data, indent=2)}
Verification Results: {json.dumps(verification_result, indent=2)}
Valuation Results: {json.dumps(valuation_result, indent=2)}

Generate a clear, structured report covering:
1. Property Overview
2. Ownership Verification Status
3. Valuation Summary
4. Risk Assessment
5. Loan Eligibility Recommendation
6. Required Actions/Documents

Format as a professional report suitable for loan officers.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": report_prompt}
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating property report: {e}")
            return f"Error generating report: {e}"
    
    def _get_empty_property_template(self) -> Dict[str, Any]:
        """Return empty property data template"""
        return {
            "document_analysis": {
                "document_type": "",
                "language_detected": "",
                "confidence": "low",
                "completeness": "incomplete"
            },
            "property_details": {
                "survey_number": "",
                "sub_division": "",
                "village": "",
                "taluk": "",
                "district": "",
                "total_area": "",
                "area_unit": "",
                "land_classification": "",
                "land_type": "",
                "boundaries": {
                    "north": "",
                    "south": "",
                    "east": "",
                    "west": ""
                }
            },
            "ownership_details": {
                "owner_name": "",
                "father_name": "",
                "ownership_type": "",
                "share_details": "",
                "acquisition_date": "",
                "acquisition_mode": ""
            },
            "revenue_details": {
                "revenue_village": "",
                "revenue_survey_number": "",
                "assessment_number": "",
                "annual_assessment": "",
                "water_rate": "",
                "total_assessment": ""
            },
            "verification_fields": {
                "registration_date": "",
                "registration_number": "",
                "sub_registrar_office": "",
                "stamp_duty_paid": "",
                "registration_fee_paid": ""
            },
            "encumbrances": {
                "mortgages": [],
                "loans_against_property": [],
                "legal_disputes": [],
                "government_dues": ""
            }
        }

# Example usage and testing
if __name__ == "__main__":
    agent = PropertyVerificationAgent()
    
    # Test property document parsing
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
    """
    
    parsed_data = agent.parse_property_document(sample_doc_text)
    print("Parsed Property Data:", json.dumps(parsed_data, indent=2))
    
    # Test property valuation
    valuation = agent.calculate_property_value(parsed_data)
    print("Property Valuation:", json.dumps(valuation, indent=2))
