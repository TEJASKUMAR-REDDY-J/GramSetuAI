"""
OpsGenie Agent
Operations intelligence + field staff manager for MFI operations
Assists in optimizing field visits, resolving bottlenecks, and automating reporting
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from groq import Groq
from dotenv import load_dotenv
import random
import math

# Load environment variables
load_dotenv()

class OpsGenieAgent:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
            
        self.client = Groq(api_key=self.groq_api_key)
        self.model = os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct")
        
        # Initialize ops data
        self.ops_data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'ops_data.json')
        self.ops_data = self._load_ops_data()
    
    def _load_ops_data(self) -> Dict[str, Any]:
        """Load operational data or create sample data"""
        try:
            if os.path.exists(self.ops_data_file):
                with open(self.ops_data_file, 'r') as f:
                    return json.load(f)
            else:
                return self._create_sample_ops_data()
        except Exception as e:
            print(f"Error loading ops data: {e}")
            return self._create_sample_ops_data()
    
    def _create_sample_ops_data(self) -> Dict[str, Any]:
        """Create sample operational data for demonstration"""
        
        # Generate sample field officers
        field_officers = []
        for i in range(1, 16):  # 15 field officers
            fo = {
                "fo_id": f"FO_{i:03d}",
                "name": f"Field Officer {i}",
                "phone": f"+91-9876543{i:03d}",
                "zone": f"Zone {chr(65 + (i-1)//5)}",  # Zone A, B, C
                "experience_years": random.randint(1, 8),
                "languages": ["English", "Kannada", "Hindi"][:random.randint(2, 3)],
                "assigned_villages": [f"Village_{i}_{j}" for j in range(1, random.randint(3, 7))],
                "assigned_borrowers": random.randint(80, 150),
                "current_workload": random.randint(60, 140),
                "performance_rating": round(random.uniform(3.2, 4.8), 1),
                "status": "Active"
            }
            field_officers.append(fo)
        
        # Generate sample visits and activities
        current_date = datetime.now()
        visits = []
        for i in range(100):  # 100 recent visits
            visit_date = current_date - timedelta(days=random.randint(0, 30))
            fo = random.choice(field_officers)
            
            visit = {
                "visit_id": f"V_{i+1:05d}",
                "fo_id": fo["fo_id"],
                "borrower_id": f"B_{random.randint(1000, 9999)}",
                "village": random.choice(fo["assigned_villages"]),
                "visit_date": visit_date.isoformat(),
                "visit_type": random.choice(["Collection", "Disbursement", "Follow-up", "Documentation", "Group Meeting"]),
                "status": random.choice(["Completed", "Pending", "Missed", "Rescheduled"]),
                "amount_collected": random.randint(0, 5000) if random.random() > 0.3 else 0,
                "issues_reported": random.choice([[], ["Payment delay"], ["Documentation missing"], ["Customer unavailable"], ["Technical issue"]]),
                "travel_time_hours": round(random.uniform(0.5, 4.0), 1),
                "zone": fo["zone"]
            }
            visits.append(visit)
        
        ops_data = {
            "field_officers": field_officers,
            "visits": visits,
            "zones": {
                "Zone A": {"villages": 15, "borrowers": 450, "avg_distance_km": 25},
                "Zone B": {"villages": 12, "borrowers": 380, "avg_distance_km": 30},
                "Zone C": {"villages": 18, "borrowers": 520, "avg_distance_km": 35}
            },
            "performance_metrics": {
                "avg_collections_per_visit": 2850,
                "avg_visits_per_day": 6.2,
                "target_monthly_visits": 120,
                "avg_travel_time": 2.1
            },
            "last_updated": current_date.isoformat()
        }
        
        # Save to file
        os.makedirs(os.path.dirname(self.ops_data_file), exist_ok=True)
        with open(self.ops_data_file, 'w') as f:
            json.dump(ops_data, f, indent=2, default=str)
        
        return ops_data
    
    def track_field_officer_productivity(self, fo_id: str = "", zone: str = "", time_period_days: int = 30) -> Dict[str, Any]:
        """Track field officer productivity and performance metrics"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=time_period_days)
        
        # Filter field officers
        field_officers = self.ops_data["field_officers"]
        if fo_id:
            field_officers = [fo for fo in field_officers if fo["fo_id"] == fo_id]
        elif zone:
            field_officers = [fo for fo in field_officers if fo["zone"] == zone]
        
        # Filter visits in time period
        visits = []
        for visit in self.ops_data["visits"]:
            visit_date = datetime.fromisoformat(visit["visit_date"].replace('Z', '+00:00'))
            if start_date <= visit_date <= end_date:
                if fo_id and visit["fo_id"] != fo_id:
                    continue
                if zone and visit["zone"] != zone:
                    continue
                visits.append(visit)
        
        # Calculate productivity metrics
        productivity_report = []
        
        for fo in field_officers:
            fo_visits = [v for v in visits if v["fo_id"] == fo["fo_id"]]
            
            completed_visits = [v for v in fo_visits if v["status"] == "Completed"]
            missed_visits = [v for v in fo_visits if v["status"] == "Missed"]
            total_collections = sum(v["amount_collected"] for v in completed_visits)
            total_travel_time = sum(v["travel_time_hours"] for v in fo_visits)
            
            productivity = {
                "fo_id": fo["fo_id"],
                "name": fo["name"],
                "zone": fo["zone"],
                "experience_years": fo["experience_years"],
                "assigned_borrowers": fo["assigned_borrowers"],
                "current_workload": fo["current_workload"],
                "performance_rating": fo["performance_rating"],
                "period_metrics": {
                    "total_visits": len(fo_visits),
                    "completed_visits": len(completed_visits),
                    "missed_visits": len(missed_visits),
                    "completion_rate": len(completed_visits) / max(len(fo_visits), 1),
                    "total_collections": total_collections,
                    "avg_collection_per_visit": total_collections / max(len(completed_visits), 1),
                    "total_travel_time": total_travel_time,
                    "visits_per_day": len(fo_visits) / time_period_days,
                    "efficiency_score": self._calculate_efficiency_score(fo, fo_visits, completed_visits)
                },
                "workload_status": self._assess_workload_status(fo, fo_visits),
                "performance_flags": self._identify_performance_flags(fo, fo_visits, completed_visits)
            }
            
            productivity_report.append(productivity)
        
        # Sort by efficiency score
        productivity_report.sort(key=lambda x: x["period_metrics"]["efficiency_score"], reverse=True)
        
        return {
            "analysis_period": f"{time_period_days} days",
            "total_officers_analyzed": len(productivity_report),
            "zone_filter": zone,
            "fo_filter": fo_id,
            "productivity_report": productivity_report,
            "summary_metrics": self._calculate_summary_metrics(productivity_report)
        }
    
    def _calculate_efficiency_score(self, fo: Dict[str, Any], fo_visits: List[Dict[str, Any]], completed_visits: List[Dict[str, Any]]) -> float:
        """Calculate efficiency score for field officer"""
        
        if not fo_visits:
            return 0.0
        
        # Factors for efficiency calculation
        completion_rate = len(completed_visits) / len(fo_visits)
        collections_factor = min(sum(v["amount_collected"] for v in completed_visits) / 100000, 1.0)  # Normalize to 1L
        experience_factor = min(fo["experience_years"] / 5, 1.0)  # Max factor at 5+ years
        workload_factor = max(0, 1 - (fo["current_workload"] / fo["assigned_borrowers"]))  # Penalty for overload
        
        # Weighted efficiency score
        efficiency = (
            completion_rate * 0.4 +
            collections_factor * 0.3 +
            experience_factor * 0.2 +
            workload_factor * 0.1
        )
        
        return round(efficiency, 3)
    
    def _assess_workload_status(self, fo: Dict[str, Any], fo_visits: List[Dict[str, Any]]) -> str:
        """Assess workload status of field officer"""
        
        workload_ratio = fo["current_workload"] / fo["assigned_borrowers"]
        daily_visits = len(fo_visits) / 30  # Assuming 30-day period
        
        if workload_ratio > 1.2 or daily_visits > 8:
            return "Overloaded"
        elif workload_ratio > 1.0 or daily_visits > 6:
            return "High Load"
        elif workload_ratio < 0.6 or daily_visits < 3:
            return "Under-utilized"
        else:
            return "Optimal"
    
    def _identify_performance_flags(self, fo: Dict[str, Any], fo_visits: List[Dict[str, Any]], completed_visits: List[Dict[str, Any]]) -> List[str]:
        """Identify performance flags for field officer"""
        
        flags = []
        
        if not fo_visits:
            flags.append("No recent activity")
            return flags
        
        completion_rate = len(completed_visits) / len(fo_visits)
        missed_visits = [v for v in fo_visits if v["status"] == "Missed"]
        
        if completion_rate < 0.7:
            flags.append("Low completion rate")
        
        if len(missed_visits) > 5:
            flags.append("High missed visits")
        
        if fo["current_workload"] > fo["assigned_borrowers"] * 1.3:
            flags.append("Severely overloaded")
        
        avg_collection = sum(v["amount_collected"] for v in completed_visits) / max(len(completed_visits), 1)
        if avg_collection < 2000:
            flags.append("Low collections per visit")
        
        if fo["performance_rating"] < 3.5:
            flags.append("Below average rating")
        
        return flags
    
    def _calculate_summary_metrics(self, productivity_report: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics for the team"""
        
        if not productivity_report:
            return {}
        
        total_visits = sum(fo["period_metrics"]["total_visits"] for fo in productivity_report)
        total_completed = sum(fo["period_metrics"]["completed_visits"] for fo in productivity_report)
        total_collections = sum(fo["period_metrics"]["total_collections"] for fo in productivity_report)
        
        return {
            "total_visits": total_visits,
            "total_completed_visits": total_completed,
            "overall_completion_rate": total_completed / max(total_visits, 1),
            "total_collections": total_collections,
            "avg_efficiency_score": sum(fo["period_metrics"]["efficiency_score"] for fo in productivity_report) / len(productivity_report),
            "officers_overloaded": len([fo for fo in productivity_report if fo["workload_status"] == "Overloaded"]),
            "officers_with_flags": len([fo for fo in productivity_report if fo["performance_flags"]])
        }
    
    def optimize_field_routes(self, zone: str = "", max_visits_per_day: int = 6) -> Dict[str, Any]:
        """Optimize field visit routes and schedules"""
        
        # Get pending visits and follow-ups
        pending_visits = []
        current_date = datetime.now()
        
        for visit in self.ops_data["visits"]:
            if visit["status"] in ["Pending", "Rescheduled"]:
                visit_date = datetime.fromisoformat(visit["visit_date"].replace('Z', '+00:00'))
                if visit_date <= current_date + timedelta(days=7):  # Next 7 days
                    if not zone or visit["zone"] == zone:
                        pending_visits.append(visit)
        
        # Group by field officer and zone
        fo_schedules = {}
        
        for visit in pending_visits:
            fo_id = visit["fo_id"]
            if fo_id not in fo_schedules:
                fo_schedules[fo_id] = {
                    "fo_info": next((fo for fo in self.ops_data["field_officers"] if fo["fo_id"] == fo_id), {}),
                    "visits": []
                }
            fo_schedules[fo_id]["visits"].append(visit)
        
        # Optimize routes for each FO
        optimized_routes = []
        
        for fo_id, schedule in fo_schedules.items():
            fo_info = schedule["fo_info"]
            visits = schedule["visits"]
            
            # Group visits by village for efficiency
            village_groups = {}
            for visit in visits:
                village = visit["village"]
                if village not in village_groups:
                    village_groups[village] = []
                village_groups[village].append(visit)
            
            # Create daily schedules
            daily_schedules = []
            remaining_visits = list(visits)
            day = 0
            
            while remaining_visits and day < 7:
                daily_visits = []
                visits_today = 0
                
                # Prioritize high-priority visits
                priority_visits = [v for v in remaining_visits if v["visit_type"] in ["Collection", "Follow-up"]]
                regular_visits = [v for v in remaining_visits if v not in priority_visits]
                
                # Add priority visits first
                for visit in priority_visits[:max_visits_per_day//2]:
                    daily_visits.append(visit)
                    remaining_visits.remove(visit)
                    visits_today += 1
                
                # Add regular visits to fill the day
                for visit in regular_visits:
                    if visits_today >= max_visits_per_day:
                        break
                    daily_visits.append(visit)
                    remaining_visits.remove(visit)
                    visits_today += 1
                
                if daily_visits:
                    # Sort by village to minimize travel
                    daily_visits.sort(key=lambda x: x["village"])
                    
                    daily_schedules.append({
                        "day": day + 1,
                        "date": (current_date + timedelta(days=day)).strftime('%Y-%m-%d'),
                        "visits": daily_visits,
                        "estimated_travel_time": self._estimate_travel_time(daily_visits),
                        "total_visits": len(daily_visits)
                    })
                
                day += 1
            
            optimized_routes.append({
                "fo_id": fo_id,
                "fo_name": fo_info.get("name", "Unknown"),
                "zone": fo_info.get("zone", "Unknown"),
                "total_pending_visits": len(visits),
                "scheduled_visits": sum(len(day["visits"]) for day in daily_schedules),
                "unscheduled_visits": len(remaining_visits),
                "daily_schedules": daily_schedules,
                "optimization_score": self._calculate_route_optimization_score(daily_schedules)
            })
        
        return {
            "optimization_date": current_date.isoformat(),
            "zone_filter": zone,
            "max_visits_per_day": max_visits_per_day,
            "total_officers": len(optimized_routes),
            "optimized_routes": optimized_routes,
            "summary": {
                "total_pending_visits": sum(route["total_pending_visits"] for route in optimized_routes),
                "total_scheduled": sum(route["scheduled_visits"] for route in optimized_routes),
                "optimization_coverage": sum(route["scheduled_visits"] for route in optimized_routes) / max(sum(route["total_pending_visits"] for route in optimized_routes), 1)
            }
        }
    
    def _estimate_travel_time(self, visits: List[Dict[str, Any]]) -> float:
        """Estimate travel time for daily visits"""
        if len(visits) <= 1:
            return 0.5  # Base travel time
        
        # Estimate based on village changes and visit types
        village_changes = len(set(visit["village"] for visit in visits))
        base_time = village_changes * 0.5  # 30 min per village change
        visit_time = len(visits) * 0.3  # 20 min per visit
        
        return round(base_time + visit_time, 1)
    
    def _calculate_route_optimization_score(self, daily_schedules: List[Dict[str, Any]]) -> float:
        """Calculate optimization score for route efficiency"""
        if not daily_schedules:
            return 0.0
        
        total_visits = sum(len(day["visits"]) for day in daily_schedules)
        total_travel_time = sum(day["estimated_travel_time"] for day in daily_schedules)
        
        # Better score for more visits with less travel time
        if total_travel_time == 0:
            return 1.0
        
        efficiency = total_visits / total_travel_time
        return min(efficiency / 3, 1.0)  # Normalize to 0-1 scale
    
    def detect_operational_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect operational bottlenecks and critical delays"""
        
        bottlenecks = []
        current_date = datetime.now()
        
        # Analyze field officer workloads
        overloaded_officers = []
        for fo in self.ops_data["field_officers"]:
            if fo["current_workload"] > fo["assigned_borrowers"] * 1.2:
                overloaded_officers.append(fo)
        
        if overloaded_officers:
            bottlenecks.append({
                "type": "Resource Bottleneck",
                "severity": "High",
                "description": f"{len(overloaded_officers)} field officers are overloaded",
                "affected_officers": [fo["fo_id"] for fo in overloaded_officers],
                "impact": "Reduced visit quality, missed collections, staff burnout",
                "recommended_action": "Redistribute workload or hire additional staff"
            })
        
        # Analyze missed visits
        recent_visits = [v for v in self.ops_data["visits"] 
                        if datetime.fromisoformat(v["visit_date"].replace('Z', '+00:00')) >= current_date - timedelta(days=7)]
        missed_visits = [v for v in recent_visits if v["status"] == "Missed"]
        
        if len(missed_visits) > len(recent_visits) * 0.15:  # More than 15% missed
            bottlenecks.append({
                "type": "Process Bottleneck",
                "severity": "Medium",
                "description": f"High missed visit rate: {len(missed_visits)}/{len(recent_visits)} ({len(missed_visits)/max(len(recent_visits), 1)*100:.1f}%)",
                "affected_zones": list(set(v["zone"] for v in missed_visits)),
                "impact": "Collection delays, borrower dissatisfaction",
                "recommended_action": "Review scheduling process and field officer training"
            })
        
        # Analyze zone performance
        zone_performance = {}
        for visit in recent_visits:
            zone = visit["zone"]
            if zone not in zone_performance:
                zone_performance[zone] = {"total": 0, "completed": 0, "collections": 0}
            
            zone_performance[zone]["total"] += 1
            if visit["status"] == "Completed":
                zone_performance[zone]["completed"] += 1
                zone_performance[zone]["collections"] += visit["amount_collected"]
        
        for zone, metrics in zone_performance.items():
            completion_rate = metrics["completed"] / max(metrics["total"], 1)
            if completion_rate < 0.7:  # Less than 70% completion
                bottlenecks.append({
                    "type": "Geographic Bottleneck",
                    "severity": "Medium",
                    "description": f"Poor performance in {zone}: {completion_rate:.1%} completion rate",
                    "affected_zones": [zone],
                    "impact": "Regional collection shortfall",
                    "recommended_action": f"Focus management attention on {zone}, review local challenges"
                })
        
        return bottlenecks
    
    def generate_weekly_ops_report(self, mfi_id: str, zone_filter: str = "") -> str:
        """Generate comprehensive weekly operations report"""
        
        # Get productivity data
        productivity_data = self.track_field_officer_productivity(zone=zone_filter, time_period_days=7)
        
        # Get route optimization
        route_optimization = self.optimize_field_routes(zone=zone_filter)
        
        # Detect bottlenecks
        bottlenecks = self.detect_operational_bottlenecks()
        
        # Generate AI insights
        ai_insights = self._generate_ops_ai_insights(productivity_data, route_optimization, bottlenecks)
        
        # Generate the report
        report = f"""
# ⚙️ OpsGenie Weekly Operations Report
**MFI ID**: {mfi_id}  
**Report Period**: Week ending {datetime.now().strftime('%Y-%m-%d')}  
**Zone Filter**: {zone_filter if zone_filter else 'All Zones'}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📊 Field Officer Performance Overview

**Officers Analyzed**: {productivity_data['total_officers_analyzed']}  
**Overall Completion Rate**: {productivity_data['summary_metrics'].get('overall_completion_rate', 0)*100:.1f}%  
**Total Collections**: ₹{productivity_data['summary_metrics'].get('total_collections', 0):,.2f}  
**Average Efficiency Score**: {productivity_data['summary_metrics'].get('avg_efficiency_score', 0):.3f}

### 🏆 Top Performers:
"""
        
        top_performers = productivity_data['productivity_report'][:3]
        for i, fo in enumerate(top_performers, 1):
            report += f"""
{i}. **{fo['name']}** ({fo['fo_id']}) - {fo['zone']}
   - Efficiency Score: {fo['period_metrics']['efficiency_score']:.3f}
   - Completion Rate: {fo['period_metrics']['completion_rate']*100:.1f}%
   - Collections: ₹{fo['period_metrics']['total_collections']:,.0f}
"""
        
        # Performance flags section
        flagged_officers = [fo for fo in productivity_data['productivity_report'] if fo['performance_flags']]
        if flagged_officers:
            report += f"""
### ⚠️ Officers Requiring Attention ({len(flagged_officers)}):
"""
            for fo in flagged_officers:
                report += f"""
- **{fo['name']}** ({fo['fo_id']}) - {fo['workload_status']}
  Issues: {', '.join(fo['performance_flags'])}
"""
        
        report += f"""
## 🗺️ Route Optimization Summary

**Total Pending Visits**: {route_optimization['summary']['total_pending_visits']}  
**Visits Scheduled**: {route_optimization['summary']['total_scheduled']}  
**Optimization Coverage**: {route_optimization['summary']['optimization_coverage']*100:.1f}%

### 📅 Next Week Schedule Highlights:
"""
        
        for route in route_optimization['optimized_routes'][:5]:  # Top 5 officers
            report += f"""
- **{route['fo_name']}** ({route['zone']}): {route['scheduled_visits']} visits scheduled, {route['unscheduled_visits']} pending
"""
        
        report += f"""
## 🚨 Operational Bottlenecks Detected

"""
        
        if bottlenecks:
            for bottleneck in bottlenecks:
                severity_emoji = "🚨" if bottleneck['severity'] == 'High' else "⚠️" if bottleneck['severity'] == 'Medium' else "📝"
                report += f"""
### {severity_emoji} {bottleneck['type']} - {bottleneck['severity']} Priority
**Issue**: {bottleneck['description']}  
**Impact**: {bottleneck['impact']}  
**Recommended Action**: {bottleneck['recommended_action']}

"""
        else:
            report += "✅ No critical bottlenecks detected this week.\n\n"
        
        report += f"""
## 🧠 AI-Generated Operational Insights
{ai_insights}

## 📋 Action Items for Next Week

### 🎯 Immediate Priorities:
1. **Address Overloaded Officers**: {"Redistribute workload for overloaded staff" if productivity_data['summary_metrics'].get('officers_overloaded', 0) > 0 else "Monitor workload distribution"}
2. **Route Optimization**: Implement optimized schedules for {len(route_optimization['optimized_routes'])} field officers
3. **Performance Support**: Provide targeted support to {len(flagged_officers)} officers with performance flags

### 📊 Performance Targets:
- **Target Completion Rate**: >85%
- **Target Daily Visits**: 6-8 per officer
- **Target Collection Rate**: >₹3,000 per visit
- **Target Efficiency Score**: >0.7

### 🔧 Process Improvements:
- Review and update field visit procedures
- Implement real-time visit tracking
- Enhance officer training programs
- Optimize zone assignments based on performance data

## 📈 Key Performance Indicators (Weekly Trend)

| Metric | This Week | Target | Status |
|--------|-----------|---------|---------|
| Completion Rate | {productivity_data['summary_metrics'].get('overall_completion_rate', 0)*100:.1f}% | 85% | {"✅" if productivity_data['summary_metrics'].get('overall_completion_rate', 0) >= 0.85 else "⚠️"} |
| Avg Collections | ₹{productivity_data['summary_metrics'].get('total_collections', 0) / max(productivity_data['summary_metrics'].get('total_completed_visits', 1), 1):,.0f} | ₹3,000 | {"✅" if productivity_data['summary_metrics'].get('total_collections', 0) / max(productivity_data['summary_metrics'].get('total_completed_visits', 1), 1) >= 3000 else "⚠️"} |
| Efficiency Score | {productivity_data['summary_metrics'].get('avg_efficiency_score', 0):.3f} | 0.700 | {"✅" if productivity_data['summary_metrics'].get('avg_efficiency_score', 0) >= 0.7 else "⚠️"} |
| Officers @ Risk | {productivity_data['summary_metrics'].get('officers_with_flags', 0)} | 0 | {"✅" if productivity_data['summary_metrics'].get('officers_with_flags', 0) == 0 else "⚠️"} |

---
*Report generated by OpsGenie Agent - GramSetuAI MFI Platform*
"""
        
        return report
    
    def _generate_ops_ai_insights(self, productivity_data: Dict[str, Any], route_data: Dict[str, Any], bottlenecks: List[Dict[str, Any]]) -> str:
        """Generate AI-powered operational insights"""
        
        try:
            completion_rate = productivity_data['summary_metrics'].get('overall_completion_rate', 0)
            efficiency_score = productivity_data['summary_metrics'].get('avg_efficiency_score', 0)
            overloaded_count = productivity_data['summary_metrics'].get('officers_overloaded', 0)
            optimization_coverage = route_data['summary']['optimization_coverage']
            
            bottleneck_summary = f"{len(bottlenecks)} bottlenecks identified" if bottlenecks else "no major bottlenecks"
            
            prompt = f"""
You are a senior operations manager at a leading microfinance institution in India with 15+ years of field operations experience.

Analyze this operational data and provide strategic insights:

TEAM PERFORMANCE:
- Total Field Officers: {productivity_data['total_officers_analyzed']}
- Overall Completion Rate: {completion_rate:.1%}
- Average Efficiency Score: {efficiency_score:.3f}
- Officers Overloaded: {overloaded_count}
- Route Optimization Coverage: {optimization_coverage:.1%}
- Operational Issues: {bottleneck_summary}

Based on your experience with Indian microfinance field operations, provide:
1. KEY OPERATIONAL INSIGHTS (2-3 critical observations)
2. EFFICIENCY IMPROVEMENT STRATEGIES (2-3 actionable recommendations)
3. STAFF MANAGEMENT PRIORITIES (1-2 immediate focus areas)
4. SCALABILITY RECOMMENDATIONS (if performance allows growth)

Keep insights practical for Indian rural microfinance operations.
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

# Example usage
if __name__ == "__main__":
    ops_agent = OpsGenieAgent()
    
    # Test weekly report generation
    test_report = ops_agent.generate_weekly_ops_report(
        mfi_id="MFI_20241201_123456",
        zone_filter="Zone A"
    )
    
    print(test_report)
