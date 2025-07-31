"""
PolicyPulse Advisor Agent
Compliance + scheme-aware strategic advisor for MFI operations
Keeps MFIs updated with government policies and schemes
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PolicyPulseAdvisor:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.client = Groq(api_key=self.groq_api_key)
        self.model = os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct")
        
        # Initialize policy database
        self.policy_db_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'policy_database.json')
        self.policies = self._load_policy_database()
    
    def _load_policy_database(self) -> Dict[str, Any]:
        """Load policy database or create sample data"""
        try:
            if os.path.exists(self.policy_db_file):
                with open(self.policy_db_file, 'r') as f:
                    return json.load(f)
            else:
                return self._create_sample_policy_data()
        except Exception as e:
            print(f"Error loading policy database: {e}")
            return self._create_sample_policy_data()
    
    def _create_sample_policy_data(self) -> Dict[str, Any]:
        """Create sample policy data for demonstration"""
        sample_policies = {
            "government_schemes": [
                {
                    "scheme_id": "PMMY_2024",
                    "name": "Pradhan Mantri MUDRA Yojana",
                    "type": "Government Scheme",
                    "agency": "MUDRA",
                    "launch_date": "2024-01-01",
                    "validity": "2024-12-31",
                    "target_segment": "Micro enterprises",
                    "loan_amount_range": {"min": 50000, "max": 1000000},
                    "interest_subsidy": "Up to 3% interest subsidy",
                    "eligibility_criteria": [
                        "Non-farm income generating activities",
                        "Business establishment or expansion",
                        "Working capital requirements"
                    ],
                    "documentation": [
                        "Aadhaar Card",
                        "Business Plan",
                        "Income Proof"
                    ],
                    "states_applicable": ["All States"],
                    "status": "Active",
                    "impact_summary": "Direct lending support for micro enterprises"
                },
                {
                    "scheme_id": "SVAMITVA_2024",
                    "name": "SVAMITVA Scheme - Property Cards",
                    "type": "Land Rights Scheme",
                    "agency": "Ministry of Panchayati Raj",
                    "launch_date": "2024-04-01",
                    "validity": "Ongoing",
                    "target_segment": "Rural property owners",
                    "loan_amount_range": {"min": 0, "max": 0},
                    "interest_subsidy": "Property documentation support",
                    "eligibility_criteria": [
                        "Rural residential property owners",
                        "Village within SVAMITVA coverage"
                    ],
                    "documentation": [
                        "Property Survey Records",
                        "Village Revenue Records"
                    ],
                    "states_applicable": ["Karnataka", "Maharashtra", "Haryana", "Uttar Pradesh"],
                    "status": "Active",
                    "impact_summary": "Property cards can be used as collateral for loans"
                },
                {
                    "scheme_id": "PMFBY_2024",
                    "name": "Pradhan Mantri Fasal Bima Yojana",
                    "type": "Insurance Scheme",
                    "agency": "Ministry of Agriculture",
                    "launch_date": "2024-01-01",
                    "validity": "2024-12-31",
                    "target_segment": "Farmers",
                    "loan_amount_range": {"min": 0, "max": 0},
                    "interest_subsidy": "Premium subsidy up to 90%",
                    "eligibility_criteria": [
                        "All farmers (tenant/sharecropper)",
                        "Notified crops in notified areas"
                    ],
                    "documentation": [
                        "Land Records",
                        "Aadhaar Card",
                        "Bank Account Details"
                    ],
                    "states_applicable": ["All States"],
                    "status": "Active",
                    "impact_summary": "Reduces agricultural loan risk through crop insurance"
                }
            ],
            "regulatory_updates": [
                {
                    "update_id": "RBI_DIR_2024_03",
                    "title": "Fair Practices Code for NBFC-MFIs",
                    "agency": "RBI",
                    "date": "2024-03-15",
                    "type": "Compliance Directive",
                    "summary": "Updated guidelines for fair lending practices",
                    "key_changes": [
                        "Enhanced borrower grievance mechanism",
                        "Mandatory financial literacy programs",
                        "Transparent pricing disclosure"
                    ],
                    "compliance_deadline": "2024-06-30",
                    "impact_on_mfis": "Medium",
                    "action_required": "Update operational procedures and staff training"
                },
                {
                    "update_id": "NABARD_CIR_2024_02",
                    "title": "Digital Lending Guidelines for MFIs",
                    "agency": "NABARD",
                    "date": "2024-02-10",
                    "type": "Operational Guidelines",
                    "summary": "Framework for digital lending operations",
                    "key_changes": [
                        "Digital KYC acceptance",
                        "e-NACH mandate guidelines",
                        "Data privacy requirements"
                    ],
                    "compliance_deadline": "2024-09-30",
                    "impact_on_mfis": "High",
                    "action_required": "Technology upgrade and process digitization"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        # Save to file
        os.makedirs(os.path.dirname(self.policy_db_file), exist_ok=True)
        with open(self.policy_db_file, 'w') as f:
            json.dump(sample_policies, f, indent=2, default=str)
        
        return sample_policies
    
    def scan_new_policies(self) -> List[Dict[str, Any]]:
        """Scan for new policies and schemes (simulated - would integrate with real APIs)"""
        # In real implementation, this would fetch from:
        # - RBI website APIs
        # - NABARD circulars
        # - Government scheme portals
        # - State government websites
        
        # For demo, return simulated new policies
        new_policies = [
            {
                "scheme_id": "KCC_DIGITAL_2024",
                "name": "Digital Kisan Credit Card Enhancement",
                "type": "Agriculture Credit Scheme",
                "agency": "NABARD",
                "launch_date": datetime.now().strftime('%Y-%m-%d'),
                "validity": "2025-12-31",
                "target_segment": "Small and marginal farmers",
                "loan_amount_range": {"min": 25000, "max": 300000},
                "interest_subsidy": "2% interest subvention",
                "eligibility_criteria": [
                    "Land holding up to 2 hectares",
                    "Digital KYC completion",
                    "Soil health card available"
                ],
                "states_applicable": ["Karnataka", "Tamil Nadu", "Andhra Pradesh"],
                "status": "Recently Launched",
                "impact_summary": "Enhanced credit access for small farmers through digital platform",
                "is_new": True
            }
        ]
        
        return new_policies
    
    def match_borrowers_with_schemes(self, mfi_id: str, state: str = "", borrower_profile_filter: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Match existing borrowers with eligible schemes"""
        
        # Load borrower data (would integrate with borrower platform)
        borrower_data = self._get_sample_borrower_data(mfi_id)
        
        # Filter schemes by state if specified
        applicable_schemes = []
        for scheme in self.policies["government_schemes"]:
            if not state or state in scheme.get("states_applicable", []) or "All States" in scheme.get("states_applicable", []):
                applicable_schemes.append(scheme)
        
        # Match borrowers with schemes
        matches = []
        total_borrowers = len(borrower_data)
        
        for scheme in applicable_schemes:
            eligible_borrowers = []
            
            for borrower in borrower_data:
                if self._check_scheme_eligibility(borrower, scheme, borrower_profile_filter):
                    eligible_borrowers.append(borrower)
            
            if eligible_borrowers:
                matches.append({
                    "scheme": scheme,
                    "eligible_borrowers": eligible_borrowers,
                    "eligibility_count": len(eligible_borrowers),
                    "eligibility_percentage": (len(eligible_borrowers) / total_borrowers) * 100
                })
        
        return {
            "total_borrowers_analyzed": total_borrowers,
            "total_schemes_checked": len(applicable_schemes),
            "matches_found": len(matches),
            "scheme_matches": matches
        }
    
    def _get_sample_borrower_data(self, mfi_id: str) -> List[Dict[str, Any]]:
        """Get sample borrower data for demonstration"""
        # In real implementation, would fetch from borrower platform
        return [
            {
                "borrower_id": "B001",
                "name": "Lakshmi Devi",
                "occupation": "Agriculture",
                "monthly_income": 15000,
                "loan_amount": 50000,
                "land_holding": 1.5,
                "business_type": "Crop cultivation",
                "state": "Karnataka"
            },
            {
                "borrower_id": "B002", 
                "name": "Ravi Kumar",
                "occupation": "Small Business",
                "monthly_income": 25000,
                "loan_amount": 75000,
                "business_type": "Grocery store",
                "state": "Karnataka"
            },
            {
                "borrower_id": "B003",
                "name": "Meera Sharma",
                "occupation": "Agriculture",
                "monthly_income": 12000,
                "loan_amount": 40000,
                "land_holding": 0.8,
                "business_type": "Vegetable farming",
                "state": "Karnataka"
            }
        ]
    
    def _check_scheme_eligibility(self, borrower: Dict[str, Any], scheme: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if borrower is eligible for a specific scheme"""
        
        # Apply borrower profile filters if specified
        if filters:
            for key, value in filters.items():
                if key in borrower and borrower[key] != value:
                    return False
        
        # Check loan amount range
        loan_range = scheme.get("loan_amount_range", {})
        borrower_loan = borrower.get("loan_amount", 0)
        if loan_range.get("min", 0) > 0 and borrower_loan < loan_range["min"]:
            return False
        if loan_range.get("max", 0) > 0 and borrower_loan > loan_range["max"]:
            return False
        
        # Check occupation/business type
        target_segment = scheme.get("target_segment", "").lower()
        borrower_occupation = borrower.get("occupation", "").lower()
        borrower_business = borrower.get("business_type", "").lower()
        
        if "agriculture" in target_segment or "farmer" in target_segment:
            if "agriculture" not in borrower_occupation and "farming" not in borrower_business:
                return False
        
        if "micro enterprise" in target_segment or "business" in target_segment:
            if "business" not in borrower_occupation and "store" not in borrower_business:
                return False
        
        # Check state applicability
        scheme_states = scheme.get("states_applicable", [])
        borrower_state = borrower.get("state", "")
        if scheme_states and "All States" not in scheme_states and borrower_state not in scheme_states:
            return False
        
        return True
    
    def get_compliance_updates(self, mfi_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get relevant compliance updates for an MFI"""
        
        relevant_updates = []
        entity_type = mfi_profile.get("basic_details", {}).get("entity_type", "")
        operating_states = mfi_profile.get("basic_details", {}).get("operating_states", "")
        
        for update in self.policies["regulatory_updates"]:
            # Check if update is relevant to MFI type
            if "NBFC" in entity_type and ("NBFC" in update["title"] or "MFI" in update["title"]):
                relevant_updates.append(update)
            elif "NGO" in entity_type and "NGO" in update["title"]:
                relevant_updates.append(update)
            elif "general" in update.get("applicability", "").lower():
                relevant_updates.append(update)
        
        return relevant_updates
    
    def generate_policy_impact_analysis(self, policy_data: Dict[str, Any], mfi_profile: Dict[str, Any]) -> str:
        """Generate AI-powered policy impact analysis"""
        
        try:
            prompt = f"""
You are a senior compliance and policy advisor for microfinance institutions in India with 15+ years of experience.

Analyze the impact of this policy/scheme on the MFI:

MFI PROFILE:
- Entity Type: {mfi_profile.get('basic_details', {}).get('entity_type', 'N/A')}
- Operating States: {mfi_profile.get('basic_details', {}).get('operating_states', 'N/A')}
- Active Borrowers: {mfi_profile.get('operational_metrics', {}).get('active_borrowers', 'N/A')}
- Target Segments: {mfi_profile.get('target_segments', {}).get('borrower_type_focus', 'N/A')}
- Primary Sectors: {mfi_profile.get('target_segments', {}).get('sector_focus', 'N/A')}

POLICY/SCHEME:
- Name: {policy_data.get('name', 'N/A')}
- Type: {policy_data.get('type', 'N/A')}
- Agency: {policy_data.get('agency', 'N/A')}
- Target Segment: {policy_data.get('target_segment', 'N/A')}
- Key Benefits: {policy_data.get('interest_subsidy', 'N/A')}

Provide analysis on:
1. RELEVANCE TO MFI (High/Medium/Low and why)
2. POTENTIAL BENEFICIARIES (estimated number from their portfolio)
3. IMPLEMENTATION STRATEGY (specific steps to leverage this policy)
4. OPERATIONAL IMPACT (changes needed in processes/systems)
5. TIMELINE FOR ACTION (immediate, short-term, long-term priorities)

Keep analysis practical and actionable for Indian microfinance operations.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"AI analysis temporarily unavailable: {str(e)}"
    
    def generate_policy_pulse_report(self, mfi_id: str, state: str = "", borrower_filters: Dict[str, Any] = {}) -> str:
        """Generate comprehensive policy pulse report"""
        
        # Load MFI profile
        try:
            from data.mfi_database import mfi_db
            mfi_profile = mfi_db.get_mfi_profile(mfi_id) or {}
        except:
            mfi_profile = {"basic_details": {"entity_type": "NBFC-MFI", "operating_states": state}}
        
        # Scan for new policies
        new_policies = self.scan_new_policies()
        
        # Match borrowers with schemes
        scheme_matches = self.match_borrowers_with_schemes(mfi_id, state, borrower_filters)
        
        # Get compliance updates
        compliance_updates = self.get_compliance_updates(mfi_profile)
        
        # Generate the report
        report = f"""
# 📋 PolicyPulse Advisor - Compliance & Scheme Update
**MFI ID**: {mfi_id}  
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**State Filter**: {state if state else 'All States'}  
**Borrower Filters**: {borrower_filters if borrower_filters else 'None'}

## 🆕 New Policies & Schemes

"""
        
        if new_policies:
            for policy in new_policies:
                impact_analysis = self.generate_policy_impact_analysis(policy, mfi_profile)
                
                report += f"""
### 🎯 {policy['name']}
**Agency**: {policy['agency']}  
**Launch Date**: {policy['launch_date']}  
**Target**: {policy['target_segment']}  
**Loan Range**: ₹{policy['loan_amount_range']['min']:,} - ₹{policy['loan_amount_range']['max']:,}  
**Benefits**: {policy['interest_subsidy']}

#### 🧠 AI Impact Analysis:
{impact_analysis}

#### 📋 Eligibility Criteria:
{chr(10).join(['- ' + criteria for criteria in policy['eligibility_criteria']])}

---
"""
        else:
            report += "No new policies or schemes identified in the current scan.\n\n"
        
        report += f"""
## 🎯 Borrower-Scheme Matching Results

**Total Borrowers Analyzed**: {scheme_matches['total_borrowers_analyzed']}  
**Schemes Evaluated**: {scheme_matches['total_schemes_checked']}  
**Matching Opportunities Found**: {scheme_matches['matches_found']}

"""
        
        if scheme_matches['matches_found'] > 0:
            for match in scheme_matches['scheme_matches']:
                scheme = match['scheme']
                count = match['eligibility_count']
                percentage = match['eligibility_percentage']
                
                report += f"""
### 📊 {scheme['name']}
- **Eligible Borrowers**: {count} ({percentage:.1f}% of portfolio)
- **Scheme Benefits**: {scheme['interest_subsidy']}
- **Loan Range**: ₹{scheme['loan_amount_range']['min']:,} - ₹{scheme['loan_amount_range']['max']:,}

**Action Items**:
- Contact eligible borrowers for scheme enrollment
- Prepare required documentation
- Coordinate with {scheme['agency']} for application process

---
"""
        else:
            report += "No immediate scheme matches found for current borrower portfolio.\n\n"
        
        report += f"""
## ⚖️ Compliance Updates

"""
        
        if compliance_updates:
            for update in compliance_updates:
                urgency = "🚨 HIGH PRIORITY" if update.get('impact_on_mfis') == 'High' else "⚠️ MEDIUM PRIORITY" if update.get('impact_on_mfis') == 'Medium' else "📝 LOW PRIORITY"
                
                report += f"""
### {urgency}: {update['title']}
**Agency**: {update['agency']}  
**Date**: {update['date']}  
**Compliance Deadline**: {update['compliance_deadline']}  
**Impact Level**: {update['impact_on_mfis']}

**Summary**: {update['summary']}

**Key Changes**:
{chr(10).join(['- ' + change for change in update['key_changes']])}

**Action Required**: {update['action_required']}

---
"""
        else:
            report += "✅ No pending compliance updates requiring immediate attention.\n\n"
        
        report += f"""
## 📈 Strategic Recommendations

### 🎯 Immediate Actions (Next 30 Days):
- Review new scheme eligibilities and notify eligible borrowers
- Assess compliance deadlines and prioritize high-impact updates
- Update borrower communication about available schemes

### 📊 Portfolio Optimization:
- Focus on schemes with highest borrower match rates
- Develop scheme-specific loan products
- Train field staff on new policy benefits

### 📋 Compliance Priorities:
- Create compliance calendar for upcoming deadlines
- Update operational procedures as per new guidelines
- Implement required technology/process changes

### 🌟 Growth Opportunities:
- Leverage government schemes to reduce interest burden for borrowers
- Use scheme benefits as competitive advantage in market
- Develop partnerships with implementing agencies

## 📞 Next Steps & Support

### For Scheme Implementation:
1. **Contact Nodal Agencies**: Reach out to respective scheme implementing agencies
2. **Documentation Preparation**: Ensure borrower documents meet scheme requirements
3. **Staff Training**: Train field officers on scheme benefits and application process
4. **Borrower Communication**: Develop communication strategy for eligible borrowers

### For Compliance:
1. **Policy Review**: Conduct detailed review of compliance requirements
2. **Gap Analysis**: Identify gaps in current procedures vs. new requirements
3. **Implementation Plan**: Create timeline for compliance implementation
4. **Monitoring Setup**: Establish tracking mechanism for compliance adherence

---
*Report generated by PolicyPulse Advisor - GramSetuAI MFI Platform*
"""
        
        return report

# Example usage
if __name__ == "__main__":
    advisor = PolicyPulseAdvisor()
    
    # Test policy pulse report
    test_report = advisor.generate_policy_pulse_report(
        mfi_id="MFI_20241201_123456",
        state="Karnataka",
        borrower_filters={"occupation": "Agriculture"}
    )
    
    print(test_report)
