"""
CreditSense Analyst Agent
Deep credit intelligence + explainable risk analysis for MFI teams
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

# Add borrower platform to path for data access
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'borrower_platform'))

class CreditSenseAnalyst:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.client = Groq(api_key=self.groq_api_key)
        self.model = os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct")
        
        # Risk thresholds and weights
        self.risk_weights = {
            'credit_score': 0.35,
            'income_stability': 0.25,
            'repayment_history': 0.20,
            'collateral_value': 0.10,
            'debt_to_income': 0.10
        }
        
        self.risk_thresholds = {
            'low': 0.75,      # Above 75% = Low Risk
            'medium': 0.50,   # 50-75% = Medium Risk
            'high': 0.25      # Below 25% = High Risk
        }
    
    def get_all_borrowers_for_mfi(self, mfi_id: str) -> List[Dict[str, Any]]:
        """Get all borrowers associated with an MFI"""
        try:
            # Load from borrower platform
            borrower_file = os.path.join(os.path.dirname(__file__), '..', '..', 'borrower_platform', 'user_data.json')
            
            if os.path.exists(borrower_file):
                with open(borrower_file, 'r') as f:
                    all_borrowers = json.load(f)
                
                # Filter borrowers for this MFI (in real system, would be database query)
                mfi_borrowers = []
                for borrower_id, data in all_borrowers.items():
                    # Add MFI association logic here
                    borrower_profile = data.copy()
                    borrower_profile['borrower_id'] = borrower_id
                    mfi_borrowers.append(borrower_profile)
                
                return mfi_borrowers
            else:
                return self._get_sample_borrower_data()
                
        except Exception as e:
            print(f"Error loading borrower data: {e}")
            return self._get_sample_borrower_data()
    
    def _get_sample_borrower_data(self) -> List[Dict[str, Any]]:
        """Generate sample borrower data for demonstration"""
        return [
            {
                "borrower_id": "BRW_001",
                "personal_details": {
                    "name": "Lakshmi Devi",
                    "age": 35,
                    "occupation": "Agriculture",
                    "monthly_income": 15000,
                    "location": "Mysore Rural, Karnataka"
                },
                "loan_application": {
                    "loan_amount": 50000,
                    "loan_purpose": "Agricultural equipment",
                    "collateral_value": 75000,
                    "requested_tenure": 18
                },
                "credit_history": {
                    "previous_loans": 2,
                    "repayment_score": 85,
                    "defaults": 0
                },
                "mfi_comments": {
                    "last_updated": "2024-07-25",
                    "updated_by": "Field Officer Rajesh",
                    "performance_notes": "Excellent repayment history, timely payments for past 2 loans"
                }
            },
            {
                "borrower_id": "BRW_002", 
                "personal_details": {
                    "name": "Ravi Kumar",
                    "age": 42,
                    "occupation": "Small Business",
                    "monthly_income": 25000,
                    "location": "Bangalore Urban, Karnataka"
                },
                "loan_application": {
                    "loan_amount": 75000,
                    "loan_purpose": "Shop expansion",
                    "collateral_value": 90000,
                    "requested_tenure": 24
                },
                "credit_history": {
                    "previous_loans": 3,
                    "repayment_score": 78,
                    "defaults": 1
                },
                "mfi_comments": {
                    "last_updated": "2024-07-20",
                    "updated_by": "Branch Manager Priya",
                    "performance_notes": "Had one delayed payment last year but recovered well. Monitor closely."
                }
            }
        ]
    
    def update_borrower_performance(self, borrower_id: str, mfi_id: str, performance_data: Dict[str, Any], updated_by: str) -> Dict[str, Any]:
        """Update borrower performance data (MFI access only)"""
        try:
            # Load current borrower data
            borrower_file = os.path.join(os.path.dirname(__file__), '..', '..', 'borrower_platform', 'user_data.json')
            
            if os.path.exists(borrower_file):
                with open(borrower_file, 'r') as f:
                    all_borrowers = json.load(f)
                
                if borrower_id in all_borrowers:
                    # Update MFI comments and performance data
                    if 'mfi_comments' not in all_borrowers[borrower_id]:
                        all_borrowers[borrower_id]['mfi_comments'] = {}
                    
                    all_borrowers[borrower_id]['mfi_comments'].update({
                        'last_updated': datetime.now().isoformat(),
                        'updated_by': updated_by,
                        'performance_notes': performance_data.get('notes', ''),
                        'repayment_adjustment': performance_data.get('repayment_score_adjustment', 0),
                        'risk_flag': performance_data.get('risk_flag', 'Normal')
                    })
                    
                    # Update credit history if provided
                    if 'credit_adjustments' in performance_data:
                        if 'credit_history' not in all_borrowers[borrower_id]:
                            all_borrowers[borrower_id]['credit_history'] = {}
                        all_borrowers[borrower_id]['credit_history'].update(performance_data['credit_adjustments'])
                    
                    # Save back to file
                    with open(borrower_file, 'w') as f:
                        json.dump(all_borrowers, f, indent=2)
                    
                    return {"success": True, "message": "Borrower performance updated successfully"}
                else:
                    return {"success": False, "error": "Borrower not found"}
            else:
                return {"success": False, "error": "Borrower database not found"}
                
        except Exception as e:
            return {"success": False, "error": f"Update failed: {str(e)}"}

    def load_borrower_data(self, borrower_id: str) -> Optional[Dict[str, Any]]:
        """Load borrower data from borrower platform"""
        try:
            # Try to load from borrower platform
            borrower_file = os.path.join(os.path.dirname(__file__), '..', '..', 'borrower_platform', 'user_data.json')
            
            if os.path.exists(borrower_file):
                with open(borrower_file, 'r') as f:
                    all_borrowers = json.load(f)
                    return all_borrowers.get(borrower_id)
            
            return None
            
        except Exception as e:
            print(f"Error loading borrower data: {e}")
            return None
    
    def calculate_risk_factors(self, borrower_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate individual risk factors for a borrower"""
        
        # Credit Score Factor (0-1 scale)
        credit_score = borrower_data.get('credit_score', 500)
        credit_score_factor = min(credit_score / 900, 1.0)  # Normalize to 0-1
        
        # Income Stability Factor
        monthly_income = borrower_data.get('monthly_income', 0)
        income_stability_factor = min(monthly_income / 100000, 1.0)  # Normalize with 1L as max
        
        # Repayment History Factor (based on available data)
        payment_history = borrower_data.get('payment_history', [])
        if payment_history:
            on_time_payments = sum(1 for payment in payment_history if payment.get('status') == 'on_time')
            repayment_factor = on_time_payments / len(payment_history)
        else:
            # Use credit score as proxy if no payment history
            repayment_factor = credit_score_factor
        
        # Collateral Value Factor
        collateral = borrower_data.get('collateral', {})
        total_collateral = sum([
            collateral.get('house_value', 0),
            collateral.get('land_value', 0),
            collateral.get('other_assets', 0)
        ])
        collateral_factor = min(total_collateral / 5000000, 1.0)  # Normalize with 50L as max
        
        # Debt-to-Income Factor
        existing_loans = borrower_data.get('existing_loans', [])
        total_emi = sum(loan.get('emi', 0) for loan in existing_loans)
        debt_to_income_ratio = total_emi / max(monthly_income, 1)
        debt_factor = max(0, 1 - debt_to_income_ratio)  # Lower debt-to-income is better
        
        return {
            'credit_score_factor': credit_score_factor,
            'income_stability_factor': income_stability_factor,
            'repayment_factor': repayment_factor,
            'collateral_factor': collateral_factor,
            'debt_factor': debt_factor,
            'raw_values': {
                'credit_score': credit_score,
                'monthly_income': monthly_income,
                'total_collateral': total_collateral,
                'debt_to_income_ratio': debt_to_income_ratio,
                'payment_history_count': len(payment_history)
            }
        }
    
    def calculate_composite_risk_score(self, risk_factors: Dict[str, Any]) -> Tuple[float, str]:
        """Calculate composite risk score and risk category"""
        
        composite_score = (
            risk_factors['credit_score_factor'] * self.risk_weights['credit_score'] +
            risk_factors['income_stability_factor'] * self.risk_weights['income_stability'] +
            risk_factors['repayment_factor'] * self.risk_weights['repayment_history'] +
            risk_factors['collateral_factor'] * self.risk_weights['collateral_value'] +
            risk_factors['debt_factor'] * self.risk_weights['debt_to_income']
        )
        
        # Determine risk category
        if composite_score >= self.risk_thresholds['low']:
            risk_category = "Low Risk"
        elif composite_score >= self.risk_thresholds['medium']:
            risk_category = "Medium Risk"
        else:
            risk_category = "High Risk"
        
        return composite_score, risk_category
    
    def identify_risk_flags(self, borrower_data: Dict[str, Any], risk_factors: Dict[str, Any]) -> List[str]:
        """Identify specific risk flags and warning signs"""
        
        flags = []
        raw_values = risk_factors['raw_values']
        
        # Credit score flags
        if raw_values['credit_score'] < 600:
            flags.append("🚨 Very Low Credit Score (< 600)")
        elif raw_values['credit_score'] < 700:
            flags.append("⚠️ Below Average Credit Score (< 700)")
        
        # Income flags
        if raw_values['monthly_income'] < 20000:
            flags.append("🚨 Very Low Monthly Income (< ₹20,000)")
        elif raw_values['monthly_income'] < 35000:
            flags.append("⚠️ Low Monthly Income (< ₹35,000)")
        
        # Debt flags
        if raw_values['debt_to_income_ratio'] > 0.6:
            flags.append("🚨 Very High Debt-to-Income Ratio (> 60%)")
        elif raw_values['debt_to_income_ratio'] > 0.4:
            flags.append("⚠️ High Debt-to-Income Ratio (> 40%)")
        
        # Collateral flags
        if raw_values['total_collateral'] == 0:
            flags.append("⚠️ No Collateral Provided")
        elif raw_values['total_collateral'] < 500000:
            flags.append("⚠️ Low Collateral Value (< ₹5L)")
        
        # Payment history flags
        if raw_values['payment_history_count'] == 0:
            flags.append("⚠️ No Payment History Available")
        
        # Age and demographic flags
        age = borrower_data.get('age', 0)
        if age < 21 or age > 65:
            flags.append("⚠️ Outside Typical Age Range for Microfinance")
        
        # Employment flags
        employment_type = borrower_data.get('employment_type', '').lower()
        if employment_type in ['unemployed', 'student']:
            flags.append("🚨 High Risk Employment Status")
        elif employment_type in ['casual', 'seasonal']:
            flags.append("⚠️ Irregular Income Source")
        
        return flags
    
    def generate_recommendations(self, borrower_data: Dict[str, Any], risk_score: float, risk_category: str, risk_flags: List[str]) -> str:
        """Generate AI-powered recommendations using LLM"""
        
        try:
            prompt = f"""
You are a senior credit analyst at a microfinance institution with 15+ years of experience in rural lending in India. 

Analyze this borrower profile and provide actionable recommendations:

BORROWER PROFILE:
- Name: {borrower_data.get('personal_details', {}).get('name', 'N/A')}
- Monthly Income: ₹{borrower_data.get('personal_details', {}).get('monthly_income', 0):,}
- Loan Amount: ₹{borrower_data.get('loan_application', {}).get('loan_amount', 0):,}
- Collateral Value: ₹{borrower_data.get('loan_application', {}).get('collateral_value', 0):,}
- Age: {borrower_data.get('personal_details', {}).get('age', 'N/A')}
- Occupation: {borrower_data.get('personal_details', {}).get('occupation', 'N/A')}
- Location: {borrower_data.get('personal_details', {}).get('location', 'N/A')}
- Previous Loans: {borrower_data.get('credit_history', {}).get('previous_loans', 0)}
- Repayment Score: {borrower_data.get('credit_history', {}).get('repayment_score', 0)}%

RISK ASSESSMENT:
- Composite Risk Score: {risk_score:.2f}/1.00
- Risk Category: {risk_category}
- Risk Flags: {', '.join(risk_flags) if risk_flags else 'None'}

MFI PERFORMANCE NOTES:
{borrower_data.get('mfi_comments', {}).get('performance_notes', 'No performance notes available')}

Please provide:
1. LENDING RECOMMENDATION (Approve/Conditional/Reject with rationale)
2. SUGGESTED LOAN AMOUNT (if approval recommended)
3. RISK MITIGATION STRATEGIES (specific actions to reduce risk)
4. MONITORING REQUIREMENTS (what to track post-disbursement)
5. ALTERNATIVE PRODUCTS (if standard loan not suitable)

Keep recommendations practical and specific to Indian microfinance context.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Unable to generate AI recommendations: {str(e)}"
    
    def simulate_what_if_scenario(self, borrower_data: Dict[str, Any], scenario: str, change_value: float) -> Dict[str, Any]:
        """Simulate what-if scenarios for risk assessment"""
        
        # Create a copy of borrower data for simulation
        sim_data = borrower_data.copy()
        
        if scenario == "income_drop":
            sim_data['monthly_income'] = borrower_data.get('monthly_income', 0) * (1 - change_value/100)
        elif scenario == "income_increase":
            sim_data['monthly_income'] = borrower_data.get('monthly_income', 0) * (1 + change_value/100)
        elif scenario == "credit_score_drop":
            sim_data['credit_score'] = borrower_data.get('credit_score', 500) - change_value
        elif scenario == "additional_debt":
            existing_loans = borrower_data.get('existing_loans', [])
            additional_emi = change_value
            existing_loans.append({'emi': additional_emi, 'type': 'simulated'})
            sim_data['existing_loans'] = existing_loans
        
        # Calculate new risk factors
        sim_risk_factors = self.calculate_risk_factors(sim_data)
        sim_score, sim_category = self.calculate_composite_risk_score(sim_risk_factors)
        
        # Calculate impact
        original_risk_factors = self.calculate_risk_factors(borrower_data)
        original_score, original_category = self.calculate_composite_risk_score(original_risk_factors)
        
        return {
            'scenario': scenario,
            'change_value': change_value,
            'original_score': original_score,
            'original_category': original_category,
            'simulated_score': sim_score,
            'simulated_category': sim_category,
            'score_change': sim_score - original_score,
            'category_change': sim_category != original_category
        }
    
    def generate_risk_report(self, borrower_id: str, recent_behavior: str = "", location: str = "", group_score: float = 0.0) -> str:
        """Generate comprehensive risk report for a borrower"""
        
        # Load borrower data
        borrower_data = self.load_borrower_data(borrower_id)
        
        if not borrower_data:
            return f"❌ Borrower ID '{borrower_id}' not found in database"
        
        # Calculate risk factors
        risk_factors = self.calculate_risk_factors(borrower_data)
        risk_score, risk_category = self.calculate_composite_risk_score(risk_factors)
        risk_flags = self.identify_risk_flags(borrower_data, risk_factors)
        
        # Generate AI recommendations
        recommendations = self.generate_recommendations(borrower_data, risk_score, risk_category, risk_flags)
        
        # Generate what-if scenarios
        income_drop_scenario = self.simulate_what_if_scenario(borrower_data, "income_drop", 30)
        credit_drop_scenario = self.simulate_what_if_scenario(borrower_data, "credit_score_drop", 50)
        
        # Format the comprehensive report
        report = f"""
# 🔍 CreditSense Risk Analysis Report
**Borrower ID**: {borrower_id}  
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Analyst**: CreditSense AI Agent  

## 📊 Risk Meter
### Overall Risk Score: {risk_score:.2f}/1.00 ({risk_score*100:.0f}%)
### Risk Category: **{risk_category}**

```
Low Risk    ████████████░░░░  {self.risk_thresholds['low']:.0%}+
Medium Risk ████████░░░░░░░░  {self.risk_thresholds['medium']:.0%}-{self.risk_thresholds['low']:.0%}
High Risk   ████░░░░░░░░░░░░  <{self.risk_thresholds['medium']:.0%}
Your Score: {"█" * int(risk_score * 16)}{"░" * (16 - int(risk_score * 16))}  {risk_score*100:.0f}%
```

## 🎯 Risk Factor Breakdown
| Factor | Score | Weight | Contribution |
|--------|-------|--------|--------------|
| Credit Score | {risk_factors['credit_score_factor']:.2f} | {self.risk_weights['credit_score']:.0%} | {risk_factors['credit_score_factor'] * self.risk_weights['credit_score']:.3f} |
| Income Stability | {risk_factors['income_stability_factor']:.2f} | {self.risk_weights['income_stability']:.0%} | {risk_factors['income_stability_factor'] * self.risk_weights['income_stability']:.3f} |
| Repayment History | {risk_factors['repayment_factor']:.2f} | {self.risk_weights['repayment_history']:.0%} | {risk_factors['repayment_factor'] * self.risk_weights['repayment_history']:.3f} |
| Collateral Value | {risk_factors['collateral_factor']:.2f} | {self.risk_weights['collateral_value']:.0%} | {risk_factors['collateral_factor'] * self.risk_weights['collateral_value']:.3f} |
| Debt Management | {risk_factors['debt_factor']:.2f} | {self.risk_weights['debt_to_income']:.0%} | {risk_factors['debt_factor'] * self.risk_weights['debt_to_income']:.3f} |

## 🚨 Risk Flags & Warning Signs
{chr(10).join(['- ' + flag for flag in risk_flags]) if risk_flags else '✅ No major risk flags identified'}

## 📈 What-If Scenario Analysis
### Scenario 1: 30% Income Drop
- **Current Risk**: {risk_score:.2f} ({risk_category})
- **After Income Drop**: {income_drop_scenario['simulated_score']:.2f} ({income_drop_scenario['simulated_category']})
- **Impact**: {income_drop_scenario['score_change']:+.3f} risk score change

### Scenario 2: Credit Score Drops by 50 Points
- **Current Risk**: {risk_score:.2f} ({risk_category})
- **After Credit Drop**: {credit_drop_scenario['simulated_score']:.2f} ({credit_drop_scenario['simulated_category']})
- **Impact**: {credit_drop_scenario['score_change']:+.3f} risk score change

## 🧠 AI-Powered Recommendations
{recommendations}

## 📝 Key Insights
- **Strongest Factor**: {max(risk_factors, key=lambda k: risk_factors[k] if k.endswith('_factor') else 0)}
- **Weakest Factor**: {min(risk_factors, key=lambda k: risk_factors[k] if k.endswith('_factor') else 1)}
- **Primary Risk**: {'Credit Quality' if risk_factors['credit_score_factor'] < 0.5 else 'Income Stability' if risk_factors['income_stability_factor'] < 0.5 else 'Debt Burden' if risk_factors['debt_factor'] < 0.5 else 'Overall Low Risk'}

## 📊 Additional Context
- **Recent Behavior**: {recent_behavior if recent_behavior else 'No recent behavior data provided'}
- **Location Context**: {location if location else borrower_data.get('state', 'Not specified')}
- **Group Score**: {group_score:.2f}/1.00 {f'({group_score*100:.0f}%)' if group_score > 0 else '(No group data)'}

---
*Report generated by CreditSense Analyst - GramSetuAI MFI Platform*
"""
        
        return report
    
    def generate_portfolio_analysis(self, mfi_id: str, risk_threshold: str = "all") -> str:
        """Generate comprehensive portfolio analysis for all borrowers of an MFI"""
        
        # Get all borrowers for this MFI
        all_borrowers = self.get_all_borrowers_for_mfi(mfi_id)
        
        if not all_borrowers:
            return "❌ No borrower data found for this MFI"
        
        # Analyze each borrower
        risk_summary = {"low": 0, "medium": 0, "high": 0}
        borrower_analyses = []
        
        for borrower in all_borrowers:
            try:
                risk_score = self.calculate_risk_score(borrower)
                
                if risk_score >= self.risk_thresholds['low']:
                    risk_category = 'LOW'
                    risk_summary["low"] += 1
                elif risk_score >= self.risk_thresholds['medium']:
                    risk_category = 'MEDIUM'
                    risk_summary["medium"] += 1
                else:
                    risk_category = 'HIGH'
                    risk_summary["high"] += 1
                
                # Filter by risk threshold if specified
                if risk_threshold != "all" and risk_category.lower() != risk_threshold.lower():
                    continue
                
                borrower_analyses.append({
                    'borrower': borrower,
                    'risk_score': risk_score,
                    'risk_category': risk_category
                })
                
            except Exception as e:
                print(f"Error analyzing borrower {borrower.get('borrower_id', 'Unknown')}: {e}")
                continue
        
        # Generate comprehensive report
        total_borrowers = len(all_borrowers)
        analyzed_borrowers = len(borrower_analyses)
        
        report = f"""
# 🔍 CreditSense Portfolio Analysis
**MFI ID**: {mfi_id}  
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Filter**: {risk_threshold.title()} Risk Borrowers  

## 📊 Portfolio Risk Overview

**Total Borrowers**: {total_borrowers}  
**Analyzed**: {analyzed_borrowers}  

### Risk Distribution:
- 🟢 **Low Risk**: {risk_summary['low']} ({(risk_summary['low']/total_borrowers*100):.1f}%)
- 🟡 **Medium Risk**: {risk_summary['medium']} ({(risk_summary['medium']/total_borrowers*100):.1f}%)  
- 🔴 **High Risk**: {risk_summary['high']} ({(risk_summary['high']/total_borrowers*100):.1f}%)

## 👥 Individual Borrower Analysis

"""
        
        for analysis in borrower_analyses[:10]:  # Show top 10 for brevity
            borrower = analysis['borrower']
            risk_score = analysis['risk_score']
            risk_category = analysis['risk_category']
            
            risk_emoji = "🟢" if risk_category == "LOW" else "🟡" if risk_category == "MEDIUM" else "🔴"
            
            personal = borrower.get('personal_details', {})
            loan = borrower.get('loan_application', {})
            credit = borrower.get('credit_history', {})
            mfi_notes = borrower.get('mfi_comments', {})
            
            report += f"""
### {risk_emoji} {personal.get('name', 'Unknown')} (ID: {borrower.get('borrower_id', 'N/A')})

**Risk Score**: {risk_score:.2f}/1.00 ({risk_category} RISK)  
**Loan Amount**: ₹{loan.get('loan_amount', 0):,}  
**Monthly Income**: ₹{personal.get('monthly_income', 0):,}  
**Repayment Score**: {credit.get('repayment_score', 0)}%  
**Previous Loans**: {credit.get('previous_loans', 0)}  

**MFI Notes**: {mfi_notes.get('performance_notes', 'No notes available')}  
**Last Updated**: {mfi_notes.get('last_updated', 'Never')} by {mfi_notes.get('updated_by', 'Unknown')}

---
"""
        
        if analyzed_borrowers > 10:
            report += f"\n*Showing top 10 borrowers. Total analyzed: {analyzed_borrowers}*\n"
        
        report += f"""
## 🎯 Portfolio Recommendations

### Risk Management Actions:
- **High Risk Borrowers** ({risk_summary['high']}): Require immediate attention and monitoring
- **Medium Risk Borrowers** ({risk_summary['medium']}): Regular check-ins and support
- **Low Risk Borrowers** ({risk_summary['low']}): Consider for loan amount increases

### Next Steps:
1. **Update Performance Data**: Use the update function for borrowers with new payment information
2. **Risk Mitigation**: Focus on high-risk borrowers for intervention
3. **Portfolio Growth**: Leverage low-risk borrowers for business expansion
"""
        return analysis_text

    def analyze_loan_application(self, borrower_data: Dict[str, Any], loan_amount: float, loan_purpose: str, collateral: str = "", credit_score: int = 650) -> Dict[str, Any]:
        """Comprehensive analysis of a loan application for MFI decision-making"""
        try:
            # Calculate basic metrics
            monthly_income = borrower_data.get('monthly_income', 0)
            monthly_expenses = borrower_data.get('monthly_expenses', 0)
            net_income = monthly_income - monthly_expenses
            
            # Calculate affordability (assuming 12% annual interest, 12 months)
            monthly_rate = 0.12 / 12
            estimated_emi = loan_amount * monthly_rate * (1 + monthly_rate)**12 / ((1 + monthly_rate)**12 - 1)
            
            # Risk assessment
            if credit_score >= 750 and estimated_emi <= net_income * 0.3:
                recommendation = "APPROVED"
                suggested_rate = 12.0
            elif credit_score >= 650 and estimated_emi <= net_income * 0.4:
                recommendation = "APPROVED WITH CONDITIONS" 
                suggested_rate = 15.0
            else:
                recommendation = "REQUIRES REVIEW"
                suggested_rate = 18.0
            
            return {
                'credit_assessment': f"Credit Score: {credit_score}/900, Monthly Income: Rs.{monthly_income:,}, Net Income: Rs.{net_income:,}, Estimated EMI: Rs.{estimated_emi:,.0f}",
                'risk_factors': f"Income Coverage: {net_income/estimated_emi:.1f}x EMI, Loan Purpose: {loan_purpose}",
                'recommendation': f"DECISION: {recommendation}",
                'suggested_terms': f"Recommended Amount: Rs.{loan_amount:,}, Interest Rate: {suggested_rate}% per annum"
            }
            
        except Exception as e:
            return {
                'credit_assessment': f"Error in assessment: {e}",
                'risk_factors': "Could not calculate",
                'recommendation': "MANUAL REVIEW REQUIRED",
                'suggested_terms': "Please review manually"
            }
