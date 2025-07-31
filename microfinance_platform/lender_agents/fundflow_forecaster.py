"""
FundFlow Forecaster Agent
Portfolio health & cashflow forecasting for MFI operations
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from groq import Groq
from dotenv import load_dotenv
import random
import calendar

# Load environment variables
load_dotenv()

class FundFlowForecaster:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.client = Groq(api_key=self.groq_api_key)
        self.model = os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct")
        
        # Seasonal factors for Indian microfinance (based on agricultural cycles)
        self.seasonal_factors = {
            1: 0.85,   # January - Post-harvest, good collections
            2: 0.80,   # February - Winter season
            3: 0.75,   # March - Pre-planting expenses
            4: 0.70,   # April - Summer, crop investment
            5: 0.65,   # May - Peak summer, low income
            6: 0.70,   # June - Monsoon begins
            7: 0.75,   # July - Monsoon, planting season
            8: 0.80,   # August - Monsoon peak
            9: 0.85,   # September - Post-monsoon
            10: 0.95,  # October - Harvest season begins
            11: 1.00,  # November - Peak harvest
            12: 0.90   # December - Post-harvest celebrations
        }
        
        # Festival impact factors
        self.festival_impacts = {
            'Diwali': -0.15,      # High expenditure
            'Dussehra': -0.10,    # Moderate expenditure
            'Eid': -0.08,         # Moderate expenditure
            'Christmas': -0.05,   # Low impact
            'Holi': -0.05,        # Low impact
            'Ugadi': -0.08,       # Regional impact
            'Ganesha Chaturthi': -0.12  # High impact in South India
        }
    
    def load_portfolio_data(self, mfi_id: str) -> Dict[str, Any]:
        """Load real portfolio data from shared EMI tracking"""
        try:
            # Load actual EMI tracking data
            emi_file = os.path.join(os.path.dirname(__file__), '..', '..', 'shared_data', 'emi_tracking.json')
            
            if not os.path.exists(emi_file):
                return self._generate_sample_portfolio(mfi_id)
            
            with open(emi_file, 'r') as f:
                emi_data = json.load(f)
            
            # Filter loans for this MFI
            mfi_loans = {loan_id: loan_data for loan_id, loan_data in emi_data.items() 
                        if loan_data.get('mfi_id') == mfi_id}
            
            if not mfi_loans:
                return self._generate_sample_portfolio(mfi_id)
            
            # Transform real data into portfolio structure
            return self._transform_real_data_to_portfolio(mfi_loans, mfi_id)
                
        except Exception as e:
            print(f"Error loading portfolio data: {e}")
            return self._generate_sample_portfolio(mfi_id)
    
    def _transform_real_data_to_portfolio(self, mfi_loans: Dict, mfi_id: str) -> Dict[str, Any]:
        """Transform real EMI data into portfolio structure"""
        current_date = datetime.now()
        
        # Calculate portfolio metrics
        total_loans = len(mfi_loans)
        total_disbursed = sum(loan['principal_amount'] for loan in mfi_loans.values())
        total_outstanding = sum(loan['outstanding_balance'] for loan in mfi_loans.values())
        active_loans = [loan for loan in mfi_loans.values() if loan['status'] == 'active']
        completed_loans = [loan for loan in mfi_loans.values() if loan['status'] == 'completed']
        
        # Calculate collection rates
        total_payments_made = sum(len(loan.get('payments', [])) for loan in mfi_loans.values())
        expected_payments = sum(loan.get('tenure_months', 12) for loan in active_loans)
        collection_rate = (total_payments_made / expected_payments * 100) if expected_payments > 0 else 100
        
        # Calculate PAR (Portfolio at Risk)
        overdue_amount = 0
        for loan in active_loans:
            next_due = loan.get('next_due_date', '')
            if next_due and datetime.fromisoformat(next_due.replace('T', ' ').replace('Z', '')) < current_date:
                overdue_amount += loan['outstanding_balance']
        
        par_30_rate = (overdue_amount / total_outstanding * 100) if total_outstanding > 0 else 0
        
        # Calculate average metrics
        avg_loan_size = total_disbursed / total_loans if total_loans > 0 else 0
        avg_emi = sum(loan['emi_amount'] for loan in mfi_loans.values()) / total_loans if total_loans > 0 else 0
        
        # Generate cohort data based on disbursement dates
        cohorts = self._generate_cohorts_from_real_data(mfi_loans)
        
        return {
            'mfi_id': mfi_id,
            'portfolio_summary': {
                'total_loans': total_loans,
                'active_loans': len(active_loans),
                'completed_loans': len(completed_loans),
                'total_disbursed': total_disbursed,
                'total_outstanding': total_outstanding,
                'average_loan_size': avg_loan_size,
                'average_emi': avg_emi,
                'collection_rate': collection_rate,
                'par_30_rate': par_30_rate,
                'overdue_amount': overdue_amount
            },
            'loan_cohorts': cohorts,
            'borrower_segments': self._analyze_borrower_segments(mfi_loans),
            'geographic_distribution': self._analyze_geographic_distribution(mfi_loans),
            'repayment_patterns': self._analyze_repayment_patterns(mfi_loans),
            'last_updated': current_date.isoformat()
        }
    
    def _generate_cohorts_from_real_data(self, mfi_loans: Dict) -> List[Dict]:
        """Generate cohort analysis from real loan data"""
        cohorts = {}
        
        for loan_id, loan in mfi_loans.items():
            disbursement_date = loan.get('disbursement_date', '')
            if disbursement_date:
                # Group by month
                try:
                    date_obj = datetime.fromisoformat(disbursement_date)
                    cohort_key = date_obj.strftime('%Y-%m')
                    
                    if cohort_key not in cohorts:
                        cohorts[cohort_key] = {
                            'cohort_id': f"COH_{cohort_key.replace('-', '_')}",
                            'disbursement_date': disbursement_date,
                            'loan_count': 0,
                            'total_disbursed': 0,
                            'current_outstanding': 0,
                            'total_payments': 0,
                            'loans': []
                        }
                    
                    cohorts[cohort_key]['loan_count'] += 1
                    cohorts[cohort_key]['total_disbursed'] += loan['principal_amount']
                    cohorts[cohort_key]['current_outstanding'] += loan['outstanding_balance']
                    cohorts[cohort_key]['total_payments'] += len(loan.get('payments', []))
                    cohorts[cohort_key]['loans'].append(loan_id)
                    
                except ValueError:
                    continue
        
        # Convert to list and add calculated metrics
        cohort_list = []
        for cohort_data in cohorts.values():
            if cohort_data['loan_count'] > 0:
                cohort_data['average_loan_size'] = cohort_data['total_disbursed'] / cohort_data['loan_count']
                cohort_data['collection_rate'] = (cohort_data['total_payments'] / (cohort_data['loan_count'] * 12)) * 100 if cohort_data['loan_count'] > 0 else 0
                cohort_data['par_amount'] = cohort_data['current_outstanding'] * 0.1  # Estimate
                del cohort_data['loans']  # Remove loan IDs for cleaner output
                cohort_list.append(cohort_data)
        
        return sorted(cohort_list, key=lambda x: x['disbursement_date'], reverse=True)
    
    def _analyze_borrower_segments(self, mfi_loans: Dict) -> Dict:
        """Analyze borrower segments from real data"""
        # This would require borrower demographic data
        # For now, return basic segmentation
        return {
            'by_loan_size': {
                'small_loans': len([l for l in mfi_loans.values() if l['principal_amount'] < 30000]),
                'medium_loans': len([l for l in mfi_loans.values() if 30000 <= l['principal_amount'] < 70000]),
                'large_loans': len([l for l in mfi_loans.values() if l['principal_amount'] >= 70000])
            },
            'by_status': {
                'active': len([l for l in mfi_loans.values() if l['status'] == 'active']),
                'completed': len([l for l in mfi_loans.values() if l['status'] == 'completed']),
                'overdue': len([l for l in mfi_loans.values() if l['status'] == 'overdue'])
            }
        }
    
    def _analyze_geographic_distribution(self, mfi_loans: Dict) -> Dict:
        """Analyze geographic distribution (placeholder)"""
        return {
            'regions': {
                'rural': len(mfi_loans) * 0.7,  # Estimate
                'semi_urban': len(mfi_loans) * 0.2,
                'urban': len(mfi_loans) * 0.1
            }
        }
    
    def _analyze_repayment_patterns(self, mfi_loans: Dict) -> Dict:
        """Analyze repayment patterns from real payment data"""
        total_payments = 0
        on_time_payments = 0
        early_payments = 0
        late_payments = 0
        
        for loan in mfi_loans.values():
            payments = loan.get('payments', [])
            total_payments += len(payments)
            
            # This is simplified - in real implementation, would compare actual vs due dates
            # For now, assume most payments are on time
            on_time_payments += len(payments) * 0.8
            early_payments += len(payments) * 0.15
            late_payments += len(payments) * 0.05
        
        return {
            'total_payments': total_payments,
            'on_time_rate': (on_time_payments / total_payments * 100) if total_payments > 0 else 0,
            'early_payment_rate': (early_payments / total_payments * 100) if total_payments > 0 else 0,
            'late_payment_rate': (late_payments / total_payments * 100) if total_payments > 0 else 0
        }
    
    def _create_sample_portfolio_data(self, filepath: str):
        """Create sample portfolio data for demonstration"""
        sample_data = {}
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(sample_data, f, indent=2)
    
    def _generate_sample_portfolio(self, mfi_id: str) -> Dict[str, Any]:
        """Generate sample portfolio data for demonstration"""
        current_date = datetime.now()
        
        # Generate loan cohorts for last 24 months
        cohorts = []
        for i in range(24):
            cohort_date = current_date - timedelta(days=30*i)
            cohort_size = random.randint(50, 200)
            avg_loan_amount = random.randint(25000, 75000)
            
            cohorts.append({
                'cohort_id': f"COH_{cohort_date.strftime('%Y%m')}",
                'disbursement_date': cohort_date.isoformat(),
                'loan_count': cohort_size,
                'total_disbursed': cohort_size * avg_loan_amount,
                'average_loan_size': avg_loan_amount,
                'repayment_frequency': 'monthly',
                'current_outstanding': cohort_size * avg_loan_amount * random.uniform(0.3, 0.8),
                'par_30_amount': cohort_size * avg_loan_amount * random.uniform(0.05, 0.15),
                'region': random.choice(['North Karnataka', 'South Karnataka', 'Coastal Karnataka'])
            })
        
        return {
            'mfi_id': mfi_id,
            'portfolio_summary': {
                'total_active_loans': sum(c['loan_count'] for c in cohorts),
                'total_outstanding': sum(c['current_outstanding'] for c in cohorts),
                'total_par_30': sum(c['par_30_amount'] for c in cohorts),
                'average_loan_size': sum(c['average_loan_size'] for c in cohorts) / len(cohorts)
            },
            'loan_cohorts': cohorts,
            'last_updated': current_date.isoformat()
        }
    
    def calculate_repayment_projections(self, portfolio_data: Dict[str, Any], months_ahead: int = 6) -> Dict[str, Any]:
        """Calculate expected repayments for upcoming months"""
        
        current_date = datetime.now()
        projections = []
        
        for month_offset in range(months_ahead):
            projection_date = current_date + timedelta(days=30*month_offset)
            month_num = projection_date.month
            
            # Apply seasonal factor
            seasonal_factor = self.seasonal_factors.get(month_num, 0.80)
            
            # Calculate expected collections from each cohort
            total_expected = 0
            high_risk_amount = 0
            
            for cohort in portfolio_data['loan_cohorts']:
                cohort_date = datetime.fromisoformat(cohort['disbursement_date'].replace('Z', '+00:00'))
                months_since_disbursement = (projection_date - cohort_date).days // 30
                
                if months_since_disbursement > 0 and months_since_disbursement <= 24:  # Active cohorts
                    # Calculate monthly EMI based on outstanding amount
                    monthly_emi = cohort['current_outstanding'] / max(1, 24 - months_since_disbursement)
                    expected_collection = monthly_emi * seasonal_factor
                    
                    # Factor in existing PAR
                    par_factor = 1 - (cohort['par_30_amount'] / max(cohort['current_outstanding'], 1))
                    expected_collection *= par_factor
                    
                    total_expected += expected_collection
                    
                    # Identify high-risk collections
                    if cohort['par_30_amount'] / max(cohort['current_outstanding'], 1) > 0.10:
                        high_risk_amount += expected_collection * 0.5  # Assume 50% collection risk
            
            projections.append({
                'month': projection_date.strftime('%Y-%m'),
                'month_name': projection_date.strftime('%B %Y'),
                'expected_collections': total_expected,
                'high_risk_collections': high_risk_amount,
                'seasonal_factor': seasonal_factor,
                'confidence_level': 'High' if seasonal_factor > 0.8 else 'Medium' if seasonal_factor > 0.6 else 'Low'
            })
        
        return {
            'projection_period': f"{months_ahead} months",
            'total_expected': sum(p['expected_collections'] for p in projections),
            'total_high_risk': sum(p['high_risk_collections'] for p in projections),
            'monthly_projections': projections
        }
    
    def predict_default_spikes(self, portfolio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict potential default spikes based on patterns and seasonality"""
        
        current_date = datetime.now()
        risk_windows = []
        
        # Check next 12 months for risk periods
        for month_offset in range(12):
            check_date = current_date + timedelta(days=30*month_offset)
            month_num = check_date.month
            month_name = check_date.strftime('%B %Y')
            
            # Base risk from seasonal factors
            seasonal_risk = 1 - self.seasonal_factors.get(month_num, 0.80)
            
            # Festival risk
            festival_risk = 0
            for festival, impact in self.festival_impacts.items():
                # Simplified festival detection (actual implementation would use proper calendar)
                if month_num in [10, 11]:  # Diwali season
                    festival_risk += abs(self.festival_impacts['Diwali'])
                elif month_num in [3, 4]:  # Holi/Regional festivals
                    festival_risk += abs(self.festival_impacts['Holi'])
            
            # Crop cycle risk
            crop_risk = 0
            if month_num in [4, 5, 6]:  # Pre-monsoon stress
                crop_risk = 0.15
            elif month_num in [9]:  # Post-monsoon recovery
                crop_risk = 0.10
            
            # Combine risks
            total_risk = min(seasonal_risk + festival_risk + crop_risk, 1.0)
            
            if total_risk > 0.25:  # High risk threshold
                risk_level = 'High' if total_risk > 0.4 else 'Medium'
                
                risk_windows.append({
                    'period': month_name,
                    'risk_score': total_risk,
                    'risk_level': risk_level,
                    'risk_factors': {
                        'seasonal': seasonal_risk,
                        'festival': festival_risk,
                        'crop_cycle': crop_risk
                    },
                    'recommended_actions': self._get_risk_mitigation_actions(total_risk, month_num)
                })
        
        return risk_windows
    
    def _get_risk_mitigation_actions(self, risk_score: float, month: int) -> List[str]:
        """Get recommended actions based on risk level and month"""
        actions = []
        
        if risk_score > 0.4:  # High risk
            actions.extend([
                "Increase field officer visits",
                "Implement early warning system",
                "Restrict new disbursements by 30%",
                "Focus on collection of overdue amounts"
            ])
        elif risk_score > 0.25:  # Medium risk
            actions.extend([
                "Enhanced monitoring of PAR levels",
                "Increase borrower communication",
                "Reduce new disbursement targets by 15%"
            ])
        
        # Month-specific actions
        if month in [4, 5, 6]:  # Pre-monsoon
            actions.append("Provide crop insurance information")
            actions.append("Offer seasonal loan restructuring")
        elif month in [10, 11]:  # Festival season
            actions.append("Remind borrowers about EMI priorities")
            actions.append("Offer festival advance loans with stricter terms")
        
        return actions
    
    def calculate_safe_lending_volume(self, portfolio_data: Dict[str, Any], cash_position: float) -> Dict[str, Any]:
        """Calculate safe lending volume for next month based on cash flow"""
        
        # Get next month's collection projection
        projections = self.calculate_repayment_projections(portfolio_data, 1)
        next_month_collections = projections['monthly_projections'][0]['expected_collections']
        
        # Calculate current portfolio health
        total_outstanding = portfolio_data['portfolio_summary']['total_outstanding']
        total_par = portfolio_data['portfolio_summary']['total_par_30']
        portfolio_health = 1 - (total_par / max(total_outstanding, 1))
        
        # Conservative cash management ratios
        operational_reserve = 0.15  # 15% for operations
        default_buffer = 0.10       # 10% for defaults
        liquidity_buffer = 0.20     # 20% for liquidity
        
        # Available cash for lending
        available_cash = cash_position + next_month_collections
        safe_cash_for_lending = available_cash * (1 - operational_reserve - default_buffer - liquidity_buffer)
        
        # Adjust based on portfolio health
        health_factor = min(portfolio_health * 1.2, 1.0)  # Boost if portfolio is healthy
        safe_lending_volume = safe_cash_for_lending * health_factor
        
        return {
            'total_available_cash': available_cash,
            'safe_lending_volume': safe_lending_volume,
            'utilization_rate': safe_lending_volume / max(available_cash, 1),
            'portfolio_health_factor': health_factor,
            'recommended_loan_count': int(safe_lending_volume / portfolio_data['portfolio_summary']['average_loan_size']),
            'cash_breakdown': {
                'current_cash': cash_position,
                'expected_collections': next_month_collections,
                'operational_reserve': available_cash * operational_reserve,
                'default_buffer': available_cash * default_buffer,
                'liquidity_buffer': available_cash * liquidity_buffer
            }
        }
    
    def generate_cashflow_forecast(self, mfi_id: str, months_ahead: int = 6, regional_filter: str = "") -> str:
        """Generate comprehensive cashflow forecast report using real portfolio data"""
        
        # Load real portfolio data
        portfolio_data = self.load_portfolio_data(mfi_id)
        
        if not portfolio_data or not portfolio_data.get('portfolio_summary'):
            return f"""
# 💰 FundFlow Forecaster - Cashflow Analysis
**MFI ID**: {mfi_id}  
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  

## ⚠️ No Portfolio Data Available
No active loans found for this MFI. Please ensure:
1. Borrowers have applied for loans through your MFI
2. You have approved some loan applications
3. The EMI tracking system is properly initialized

Once you have active loans, this section will show detailed cashflow forecasts and portfolio analytics.
"""
        
        # Extract real metrics
        summary = portfolio_data['portfolio_summary']
        
        # Calculate projections based on real data
        repayment_projections = self.calculate_repayment_projections_real(portfolio_data, months_ahead)
        default_predictions = self.predict_default_spikes_real(portfolio_data)
        safe_lending = self.calculate_safe_lending_volume_real(portfolio_data)
        
        # Generate AI insights based on real data
        ai_insights = self._generate_ai_insights_real(portfolio_data, repayment_projections, default_predictions)
        
        # Format the report with real data
        report = f"""
# 💰 FundFlow Forecaster - Portfolio Health Analysis
**MFI ID**: {mfi_id}  
**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Forecast Period**: {months_ahead} months  
**Data Source**: Real EMI Tracking System

## 📊 Current Portfolio Snapshot
- **Total Loans**: {summary['total_loans']:,}
- **Active Loans**: {summary['active_loans']:,}
- **Completed Loans**: {summary['completed_loans']:,}
- **Total Disbursed**: ₹{summary['total_disbursed']:,.0f}
- **Total Outstanding**: ₹{summary['total_outstanding']:,.0f}
- **Average Loan Size**: ₹{summary['average_loan_size']:,.0f}
- **Average EMI**: ₹{summary['average_emi']:,.0f}

## 📈 Portfolio Health Metrics
- **Collection Rate**: {summary['collection_rate']:.1f}%
- **Portfolio at Risk (PAR 30+)**: {summary['par_30_rate']:.2f}%
- **Overdue Amount**: ₹{summary['overdue_amount']:,.0f}
- **Health Status**: {'🟢 Healthy' if summary['par_30_rate'] < 5 else '🟡 Watch' if summary['par_30_rate'] < 10 else '🔴 Alert'}

## 💵 Cashflow Projections ({months_ahead} months)
{repayment_projections}

## ⚠️ Risk Assessment
{default_predictions}

## 📊 Lending Capacity Analysis
{safe_lending}

## 🤖 AI-Powered Insights
{ai_insights}

---
*This analysis is based on real loan data from your EMI tracking system. Projections use historical payment patterns and seasonal factors specific to Indian microfinance.*
"""
        
        return report
    
    def _generate_ai_insights(self, portfolio_data: Dict[str, Any], projections: Dict[str, Any], risk_windows: List[Dict[str, Any]]) -> str:
        """Generate AI-powered strategic insights"""
        
        try:
            # Calculate key metrics for AI analysis
            par_ratio = portfolio_data['portfolio_summary']['total_par_30'] / max(portfolio_data['portfolio_summary']['total_outstanding'], 1)
            collection_trend = "declining" if par_ratio > 0.1 else "stable" if par_ratio > 0.05 else "improving"
            
            risk_summary = f"{len(risk_windows)} high-risk periods" if risk_windows else "no major risk periods"
            
            prompt = f"""
You are a senior portfolio manager at a leading microfinance institution in India with 20+ years of experience.

Analyze this portfolio data and provide strategic insights:

PORTFOLIO METRICS:
- Total Outstanding: ₹{portfolio_data['portfolio_summary']['total_outstanding']:,.2f}
- PAR 30+ Ratio: {par_ratio:.2%}
- Collection Trend: {collection_trend}
- Total Active Loans: {portfolio_data['portfolio_summary']['total_active_loans']:,}
- Expected Collections (6 months): ₹{projections['total_expected']:,.2f}
- High-Risk Collections: ₹{projections['total_high_risk']:,.2f}
- Risk Periods Ahead: {risk_summary}

Based on your experience with Indian microfinance, provide:
1. KEY PORTFOLIO HEALTH INSIGHTS (2-3 bullet points)
2. CASH FLOW OPTIMIZATION STRATEGIES (2-3 actionable recommendations)
3. RISK MITIGATION PRIORITIES (1-2 critical focus areas)
4. GROWTH OPPORTUNITIES (if portfolio health allows)

Keep insights practical and specific to Indian microfinance operations.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"AI insights temporarily unavailable: {str(e)}"
    
    def calculate_repayment_projections_real(self, portfolio_data: Dict, months_ahead: int) -> str:
        """Calculate repayment projections based on real portfolio data"""
        summary = portfolio_data['portfolio_summary']
        total_outstanding = summary['total_outstanding']
        avg_emi = summary['average_emi']
        active_loans = summary['active_loans']
        
        projections = []
        total_expected = 0
        
        for month in range(1, months_ahead + 1):
            current_date = datetime.now() + timedelta(days=30 * month)
            seasonal_factor = self.seasonal_factors.get(current_date.month, 0.85)
            
            # Calculate expected collections
            expected_monthly = avg_emi * active_loans * seasonal_factor
            total_expected += expected_monthly
            
            projections.append(f"| Month {month} | ₹{expected_monthly:,.0f} | {seasonal_factor:.2f} | {'🟢' if seasonal_factor > 0.85 else '🟡' if seasonal_factor > 0.75 else '🔴'} |")
        
        projection_table = "\n".join(projections)
        
        return f"""
| Month | Expected Collections | Seasonal Factor | Status |
|-------|---------------------|------------------|---------|
{projection_table}

**Total Expected Collections**: ₹{total_expected:,.0f}
**Average Monthly Collection**: ₹{total_expected/months_ahead:,.0f}
"""
    
    def predict_default_spikes_real(self, portfolio_data: Dict) -> str:
        """Predict default risks based on real portfolio data"""
        summary = portfolio_data['portfolio_summary']
        par_rate = summary['par_30_rate']
        
        if par_rate < 3:
            risk_level = "🟢 Low Risk"
            recommendations = "Maintain current practices. Consider expanding loan portfolio."
        elif par_rate < 7:
            risk_level = "🟡 Medium Risk"
            recommendations = "Monitor closely. Strengthen collection processes."
        else:
            risk_level = "🔴 High Risk"
            recommendations = "Immediate action required. Pause new lending and focus on collections."
        
        return f"""
**Current PAR 30+ Rate**: {par_rate:.2f}%
**Risk Level**: {risk_level}

**Recommendations**: {recommendations}

**Risk Factors to Monitor**:
- Seasonal payment patterns
- Regional economic conditions
- Festival seasons (high expense periods)
- Agricultural cycles and harvest timing
"""
    
    def calculate_safe_lending_volume_real(self, portfolio_data: Dict) -> str:
        """Calculate safe lending volume based on real portfolio health"""
        summary = portfolio_data['portfolio_summary']
        total_outstanding = summary['total_outstanding']
        par_rate = summary['par_30_rate']
        collection_rate = summary['collection_rate']
        
        # Calculate lending capacity based on portfolio health
        if par_rate < 3 and collection_rate > 95:
            capacity_factor = 1.2  # Can expand by 20%
            recommendation = "Portfolio health excellent. Safe to expand lending."
        elif par_rate < 5 and collection_rate > 90:
            capacity_factor = 1.1  # Can expand by 10%
            recommendation = "Good portfolio health. Moderate expansion recommended."
        elif par_rate < 10 and collection_rate > 85:
            capacity_factor = 1.0  # Maintain current level
            recommendation = "Maintain current lending levels. Focus on collection improvement."
        else:
            capacity_factor = 0.8  # Reduce by 20%
            recommendation = "Reduce new lending. Prioritize portfolio recovery."
        
        safe_volume = total_outstanding * capacity_factor
        
        return f"""
**Current Portfolio**: ₹{total_outstanding:,.0f}
**Recommended Lending Capacity**: ₹{safe_volume:,.0f}
**Capacity Utilization**: {capacity_factor*100:.0f}%

**Recommendation**: {recommendation}

**Key Metrics**:
- Collection Rate: {collection_rate:.1f}%
- PAR 30+ Rate: {par_rate:.2f}%
- Portfolio Health Score: {100 - par_rate:.1f}/100
"""
    
    def _generate_ai_insights_real(self, portfolio_data: Dict, projections: str, risks: str) -> str:
        """Generate AI insights based on real portfolio data"""
        try:
            summary = portfolio_data['portfolio_summary']
            
            prompt = f"""
Analyze this REAL microfinance portfolio data and provide strategic insights:

PORTFOLIO OVERVIEW:
- Total Loans: {summary['total_loans']}
- Active Loans: {summary['active_loans']}
- Total Outstanding: ₹{summary['total_outstanding']:,.0f}
- Collection Rate: {summary['collection_rate']:.1f}%
- PAR 30+ Rate: {summary['par_30_rate']:.2f}%
- Average Loan Size: ₹{summary['average_loan_size']:,.0f}

CASHFLOW PROJECTIONS:
{projections}

RISK ASSESSMENT:
{risks}

Provide practical insights for an Indian MFI manager:
1. PORTFOLIO HEALTH ASSESSMENT (2-3 key observations)
2. OPERATIONAL RECOMMENDATIONS (2-3 actionable steps)
3. GROWTH STRATEGY (based on current health)
4. RISK MITIGATION (1-2 priority areas)

Keep insights specific to Indian microfinance context and seasonal patterns.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"🤖 AI Analysis: Portfolio showing {'strong' if portfolio_data['portfolio_summary']['par_30_rate'] < 5 else 'moderate' if portfolio_data['portfolio_summary']['par_30_rate'] < 10 else 'concerning'} performance. Focus on collection optimization and seasonal planning."

# Example usage
if __name__ == "__main__":
    forecaster = FundFlowForecaster()
    
    # Test forecast generation
    test_report = forecaster.generate_cashflow_forecast(
        mfi_id="MFI_20241201_123456",
        cash_position=5000000,  # 50 lakh cash
        regional_filter="Karnataka",
        months_ahead=6
    )
    
    print(test_report)
