"""
Lender Recommendation Agent
Recommends nearby NBFCs and ARCs based on user location and loan requirements
Uses OpenStreetMap API for geocoding and distance calculations
Loads NBFC/ARC data from Excel file and provides map visualization
"""

import os
import json
import pandas as pd
import requests
from typing import Dict, Any, Optional, List, Tuple
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import folium
from groq import Groq
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import get_language_prompt, generate_cache_key
from .translation_agent import TranslationAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LenderRecommendationAgent:
    def __init__(self, groq_api_key: str = None):
        """
        Initialize Lender Recommendation Agent
        
        Args:
            groq_api_key: GROQ API key (optional, loads from environment if not provided)
        """
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        self.openstreetmap_api_key = os.getenv('OPENSTREETMAP_API_KEY')
        
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables or parameters")
        
        self.client = Groq(api_key=self.groq_api_key)
        self.model = os.getenv('MODEL_NAME', "meta-llama/llama-4-maverick-17b-128e-instruct")
        self.cache = {}
        self.translator = TranslationAgent(self.groq_api_key)
        
        # Initialize geocoder
        self.geolocator = Nominatim(user_agent="microfinance_lender_agent")
        
        # Load NBFC/ARC data with sample fallback
        self.lender_data = self._load_lender_data()
        
        # Check how many lenders have coordinates
        geocoded_count = len(self.lender_data[self.lender_data['latitude'].notna()])
        print(f"Found {geocoded_count} lenders with coordinates from Excel data")
        
        # Always add sample lenders to ensure we have working data
        print("Adding sample lenders for demonstration...")
        sample_data = self._create_sample_lender_data()
        self.lender_data = pd.concat([self.lender_data, sample_data], ignore_index=True)
        
        total_with_coords = len(self.lender_data[self.lender_data['latitude'].notna()])
        print(f"Total lenders with coordinates: {total_with_coords}")
        
        # Loan type mappings
        self.loan_type_mapping = {
            "agriculture": ["agricultural", "farm", "crop", "kisan", "rural"],
            "micro_business": ["micro", "business", "sme", "msme", "enterprise"],
            "housing": ["housing", "home", "property", "real estate"],
            "education": ["education", "student", "study"],
            "vehicle": ["vehicle", "auto", "car", "bike", "transport"],
            "personal": ["personal", "individual", "consumer"],
            "gold": ["gold", "jewel", "ornament"],
            "equipment": ["equipment", "machinery", "tools"]
        }
    
    def _load_lender_data(self) -> pd.DataFrame:
        """Load NBFC and ARC data from Excel file with improved parsing"""
        try:
            excel_path = "NBFCsandARCs10012023.XLSX"
            if not os.path.exists(excel_path):
                print(f"Warning: {excel_path} not found. Creating sample data.")
                return self._create_sample_lender_data()
            
            # Try to read the Excel file
            try:
                # First, try to read and inspect the file structure
                xl = pd.ExcelFile(excel_path)
                print(f"Available sheets in Excel file: {xl.sheet_names}")
                
                # Read the first sheet (or main sheet)
                df = pd.read_excel(excel_path, sheet_name=xl.sheet_names[0])
                print(f"Original columns: {list(df.columns)}")
                
            except Exception as e:
                print(f"Error reading Excel file: {e}")
                return self._create_sample_lender_data()
            
            # Clean and standardize column names
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('/', '_').str.replace('-', '_')
            print(f"Cleaned columns: {list(df.columns)}")
            
            # Map common column name variations to standard names
            column_mapping = {
                'entity_name': 'name',
                'company_name': 'name',
                'nbfc_name': 'name',
                'institution_name': 'name',
                'entity_type': 'type',
                'company_type': 'type',
                'classification': 'type',
                'registered_office_address': 'address',
                'address': 'address',
                'registered_office': 'address',
                'place': 'city',
                'location': 'city',
                'head_office': 'city',
                'registration_date': 'registration_date',
                'date_of_registration': 'registration_date'
            }
            
            # Apply column mapping
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns and new_name not in df.columns:
                    df[new_name] = df[old_name]
                    print(f"Mapped column '{old_name}' to '{new_name}'")
            
            # Extract city/state from address if not present
            if 'address' in df.columns and ('city' not in df.columns or df['city'].isna().all()):
                print("Extracting city information from address...")
                df['city'] = df['address'].apply(self._extract_city_from_address)
            
            # Add state information if missing
            if 'state' not in df.columns:
                df['state'] = 'Karnataka'  # Default state
                print("Added default state: Karnataka")
            
            # Add default loan amounts and interest rates if missing
            if 'min_loan_amount' not in df.columns:
                df['min_loan_amount'] = 10000
            if 'max_loan_amount' not in df.columns:
                df['max_loan_amount'] = 1000000
            if 'interest_rate_min' not in df.columns:
                df['interest_rate_min'] = 10.0
            if 'interest_rate_max' not in df.columns:
                df['interest_rate_max'] = 18.0
            
            # Add specialization based on type
            if 'specialization' not in df.columns:
                df['specialization'] = df['type'].apply(self._determine_specialization)
            
            # Add coordinates if not present
            if 'latitude' not in df.columns or 'longitude' not in df.columns:
                print("Adding coordinates to lender data...")
                df = self._add_coordinates_to_lenders(df)
            
            # Clean up the data
            df = df.dropna(subset=['name'])  # Remove entries without names
            df = df[df['name'].str.strip() != '']  # Remove entries with empty names
            
            print(f"Loaded {len(df)} lenders from Excel file")
            print(f"Sample data:\n{df[['name', 'city', 'type']].head()}")
            
            return df
            
        except Exception as e:
            print(f"Error loading lender data: {e}")
            return self._create_sample_lender_data()
    
    def _extract_city_from_address(self, address: str) -> str:
        """Extract city name from address string"""
        if pd.isna(address) or not isinstance(address, str):
            return 'Unknown'
        
        # Common patterns to extract city
        address = address.strip()
        
        # Split by comma and look for city-like patterns
        parts = [part.strip() for part in address.split(',')]
        
        # Look for known cities
        known_cities = ['bangalore', 'bengaluru', 'mysore', 'tumkur', 'mandya', 'hassan', 
                       'nellore', 'guntur', 'hyderabad', 'chennai', 'coimbatore']
        
        for part in parts:
            for city in known_cities:
                if city in part.lower():
                    return part.title()
        
        # If no known city found, return the first part
        return parts[0].title() if parts else 'Unknown'
    
    def _determine_specialization(self, entity_type: str) -> str:
        """Determine specialization based on entity type"""
        if pd.isna(entity_type):
            return 'General'
        
        entity_type = str(entity_type).lower()
        
        if any(word in entity_type for word in ['bank', 'cooperative', 'rural']):
            return 'Agriculture,Rural Development,MSME'
        elif 'nbfc' in entity_type:
            return 'Personal,Business,Vehicle'
        elif 'arc' in entity_type:
            return 'Asset Reconstruction,Recovery'
        else:
            return 'General,Personal,Business'
    
    def _create_sample_lender_data(self) -> pd.DataFrame:
        """Create sample lender data for testing"""
        sample_data = [
            # Bangalore area lenders (closer to Tumkur)
            {
                'name': 'HDFC Bank - Bangalore Rural',
                'type': 'Bank',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'specialization': 'Agriculture,Rural Development',
                'min_loan_amount': 25000,
                'max_loan_amount': 1000000,
                'interest_rate_min': 10.5,
                'interest_rate_max': 15.0,
                'latitude': 12.9716,
                'longitude': 77.5946
            },
            {
                'name': 'Karnataka Bank - Tumkur Branch',
                'type': 'Bank',
                'city': 'Tumkur',
                'state': 'Karnataka',
                'specialization': 'Agriculture,MSME,Personal',
                'min_loan_amount': 10000,
                'max_loan_amount': 500000,
                'interest_rate_min': 11.0,
                'interest_rate_max': 16.0,
                'latitude': 13.3400,
                'longitude': 77.1006
            },
            {
                'name': 'State Bank of India - Tumkur',
                'type': 'Government Bank',
                'city': 'Tumkur',
                'state': 'Karnataka',
                'specialization': 'Agriculture,Rural Development,MSME',
                'min_loan_amount': 15000,
                'max_loan_amount': 2000000,
                'interest_rate_min': 9.5,
                'interest_rate_max': 14.5,
                'latitude': 13.3421,
                'longitude': 77.1025
            },
            {
                'name': 'Canara Bank - Bangalore North',
                'type': 'Government Bank',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'specialization': 'Agriculture,Housing,Business',
                'min_loan_amount': 20000,
                'max_loan_amount': 5000000,  # Increased to 50L
                'interest_rate_min': 10.0,
                'interest_rate_max': 15.5,
                'latitude': 13.0827,
                'longitude': 77.5946
            },
            {
                'name': 'State Bank of India - Commercial Branch',
                'type': 'Government Bank',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'specialization': 'Business Loans,Housing,Agriculture',
                'min_loan_amount': 50000,
                'max_loan_amount': 10000000,  # 1 Crore
                'interest_rate_min': 9.5,
                'interest_rate_max': 14.0,
                'latitude': 12.9716,
                'longitude': 77.5946
            },
            {
                'name': 'HDFC Bank - Business Banking',
                'type': 'Private Bank',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'specialization': 'Business Loans,Personal Loans,Housing',
                'min_loan_amount': 25000,
                'max_loan_amount': 7500000,  # 75L
                'interest_rate_min': 11.0,
                'interest_rate_max': 16.0,
                'latitude': 12.9351,
                'longitude': 77.6245
            },
            {
                'name': 'Karnataka Bank - Corporate Branch',
                'type': 'Regional Bank',
                'city': 'Mangalore',
                'state': 'Karnataka',
                'specialization': 'Business Loans,Agriculture,Export Finance',
                'min_loan_amount': 30000,
                'max_loan_amount': 5000000,  # 50L
                'interest_rate_min': 10.5,
                'interest_rate_max': 15.0,
                'latitude': 12.8698,
                'longitude': 74.8420
            },
            {
                'name': 'Grameen Koota Financial Services',
                'type': 'NBFC-MFI',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'specialization': 'Microfinance,Women Empowerment,Agriculture',
                'min_loan_amount': 5000,
                'max_loan_amount': 500000,  # Increased to 5L
                'interest_rate_min': 16.0,
                'interest_rate_max': 22.0,
                'latitude': 12.9141,
                'longitude': 77.6101
            },
            {
                'name': 'ESAF Small Finance Bank',
                'type': 'Small Finance Bank',
                'city': 'Mysore',
                'state': 'Karnataka',
                'specialization': 'Microfinance,Agriculture,Small Business',
                'min_loan_amount': 10000,
                'max_loan_amount': 1000000,  # Increased to 10L
                'interest_rate_min': 14.0,
                'interest_rate_max': 20.0,
                'latitude': 12.2958,
                'longitude': 76.6394
            },
            {
                'name': 'Karnataka Vikas Grameena Bank',
                'type': 'Regional Rural Bank',
                'city': 'Dharwad',
                'state': 'Karnataka',
                'specialization': 'Agriculture,Rural Development',
                'min_loan_amount': 5000,
                'max_loan_amount': 2000000,  # Increased to 20L
                'interest_rate_min': 8.5,
                'interest_rate_max': 13.0,
                'latitude': 15.4589,
                'longitude': 75.0078
            },
            {
                'name': 'Union Bank of India - Tumkur',
                'type': 'Government Bank',
                'city': 'Tumkur',
                'state': 'Karnataka',
                'specialization': 'Agriculture,MSME,Housing',
                'min_loan_amount': 12000,
                'max_loan_amount': 800000,
                'interest_rate_min': 10.5,
                'interest_rate_max': 15.0,
                'latitude': 13.3435,
                'longitude': 77.0995
            },
            {
                'name': 'Ujjivan Small Finance Bank',
                'type': 'Small Finance Bank',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'specialization': 'Microfinance,Small Business,Personal',
                'min_loan_amount': 8000,
                'max_loan_amount': 250000,
                'interest_rate_min': 15.0,
                'interest_rate_max': 21.0,
                'latitude': 12.9716,
                'longitude': 77.5946
            },
            {
                'name': 'Indian Bank - Bangalore Rural',
                'type': 'Government Bank',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'specialization': 'Agriculture,Rural Development,MSME',
                'min_loan_amount': 18000,
                'max_loan_amount': 1200000,
                'interest_rate_min': 9.8,
                'interest_rate_max': 14.8,
                'latitude': 12.9352,
                'longitude': 77.6245
            },
            {
                'name': 'Shriram Transport Finance',
                'type': 'NBFC',
                'city': 'Mangalore',
                'state': 'Karnataka',
                'specialization': 'Vehicle Finance,Transport',
                'min_loan_amount': 50000,
                'max_loan_amount': 5000000,
                'interest_rate_min': 16.0,
                'interest_rate_max': 22.0,
                'latitude': 12.9141,
                'longitude': 74.8560
            },
            {
                'name': 'Coastal Local Area Bank',
                'type': 'Local Area Bank',
                'city': 'Udupi',
                'state': 'Karnataka',
                'specialization': 'Agriculture,Fishing,Small Business',
                'min_loan_amount': 7000,
                'max_loan_amount': 150000,
                'interest_rate_min': 12.0,
                'interest_rate_max': 18.0,
                'latitude': 13.3409,
                'longitude': 74.7421
            }
        ]
        
        df = pd.DataFrame(sample_data)
        print(f"Created sample lender data with {len(df)} lenders")
        return df
    
    def _add_coordinates_to_lenders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add latitude and longitude coordinates to lender data"""
        df['latitude'] = None
        df['longitude'] = None
        
        for idx, row in df.iterrows():
            try:
                # Try to find location using city and state
                city = row.get('city', '')
                state = row.get('state', '')
                
                if city and state:
                    location_query = f"{city}, {state}, India"
                elif city:
                    location_query = f"{city}, Karnataka, India"
                else:
                    continue
                
                location = self.geolocator.geocode(location_query, timeout=10)
                if location:
                    df.at[idx, 'latitude'] = location.latitude
                    df.at[idx, 'longitude'] = location.longitude
                    print(f"Added coordinates for {row.get('name', 'Unknown')}: {location.latitude}, {location.longitude}")
                
            except Exception as e:
                print(f"Error geocoding {row.get('name', 'Unknown')}: {e}")
                continue
        
        return df
    
    def get_user_coordinates(self, user_location: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Get coordinates for user location with improved geocoding
        
        Args:
            user_location: User's complete address string
            
        Returns:
            Tuple of (latitude, longitude) or (None, None) if not found
        """
        try:
            print(f"Geocoding location: {user_location}")
            
            # First try with the complete address as provided
            location = self.geolocator.geocode(user_location, timeout=15)
            if location:
                print(f"Found coordinates: {location.latitude}, {location.longitude}")
                return location.latitude, location.longitude
            
            # If that fails, try parsing and reconstructing the address
            parts = [part.strip() for part in user_location.split(',') if part.strip()]
            
            # Try different combinations
            for i in range(len(parts)):
                if i == 0:
                    continue  # Skip first attempt as we already tried full address
                
                partial_address = ", ".join(parts[i:])
                print(f"Trying partial address: {partial_address}")
                location = self.geolocator.geocode(partial_address, timeout=10)
                if location:
                    print(f"Found coordinates with partial address: {location.latitude}, {location.longitude}")
                    return location.latitude, location.longitude
            
            # Last resort: try just the first part (usually city/village) + India
            if parts:
                simple_address = f"{parts[0]}, India"
                print(f"Trying simple address: {simple_address}")
                location = self.geolocator.geocode(simple_address, timeout=10)
                if location:
                    print(f"Found coordinates with simple address: {location.latitude}, {location.longitude}")
                    return location.latitude, location.longitude
                
            print(f"Could not geocode any variation of: {user_location}")
            return None, None
            
        except Exception as e:
            print(f"Error geocoding user location '{user_location}': {e}")
            return None, None
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        try:
            return geodesic((lat1, lon1), (lat2, lon2)).kilometers
        except:
            return float('inf')
    
    def filter_lenders_by_loan_type(self, loan_type: str) -> pd.DataFrame:
        """Filter lenders based on loan type specialization"""
        if loan_type.lower() not in self.loan_type_mapping:
            return self.lender_data  # Return all if type not recognized
        
        keywords = self.loan_type_mapping[loan_type.lower()]
        
        # Filter lenders that specialize in this loan type
        filtered_lenders = []
        for idx, row in self.lender_data.iterrows():
            specialization = str(row.get('specialization', '')).lower()
            if any(keyword in specialization for keyword in keywords):
                filtered_lenders.append(row)
        
        if filtered_lenders:
            return pd.DataFrame(filtered_lenders)
        else:
            # If no specific lenders found, return all (they might still offer the loan)
            return self.lender_data
    
    def recommend_lenders(self, user_data: Dict[str, Any], loan_request: Dict[str, Any], max_distance: float = 50) -> Dict[str, Any]:
        """
        Recommend nearby lenders based on user location and loan requirements
        Dynamically expands search radius to find minimum 10 lenders
        
        Args:
            user_data: User profile data
            loan_request: Loan requirements (amount, type, purpose)
            max_distance: Initial maximum distance in kilometers (default 50km)
            
        Returns:
            Dict containing recommended lenders and analysis
        """
        # Extract user location
        user_location = self._extract_user_location(user_data)
        if not user_location:
            return {
                "error": "User location not found in profile",
                "recommendations": [],
                "map_html": None
            }
        
        # Get user coordinates
        user_lat, user_lon = self.get_user_coordinates(user_location)
        if user_lat is None or user_lon is None:
            return {
                "error": f"Could not geocode location: {user_location}",
                "recommendations": [],
                "map_html": None
            }
        
        # Filter lenders by loan type
        loan_type = loan_request.get('type', 'personal')
        loan_amount = loan_request.get('amount', 0)
        
        relevant_lenders = self.filter_lenders_by_loan_type(loan_type)
        
        # Dynamic radius expansion to find minimum 10 lenders
        min_lenders_required = 10
        search_radiuses = [50, 100, 200, 300, 500, 1000]  # Progressive expansion
        final_recommendations = []
        final_radius = max_distance
        
        for radius in search_radiuses:
            if len(final_recommendations) >= min_lenders_required:
                break
                
            final_radius = radius
            recommendations = []
            
            # Calculate distances and filter by amount and distance
            for idx, lender in relevant_lenders.iterrows():
                lender_lat = lender.get('latitude')
                lender_lon = lender.get('longitude')
                
                if lender_lat is None or lender_lon is None:
                    continue
                
                distance = self.calculate_distance(user_lat, user_lon, lender_lat, lender_lon)
                
                # Filter by current radius
                if distance > radius:
                    continue
                
                # Filter by loan amount (if available)
                min_amount = lender.get('min_loan_amount', 0)
                max_amount = lender.get('max_loan_amount', float('inf'))
                
                amount_suitable = min_amount <= loan_amount <= max_amount
                
                recommendation = {
                    'name': lender.get('name', 'Unknown'),
                    'type': lender.get('type', 'NBFC'),
                    'city': lender.get('city', 'Unknown'),
                    'distance': round(distance, 2),
                    'distance_km': round(distance, 2),
                    'specialization': lender.get('specialization', ''),
                    'min_loan_amount': min_amount,
                    'max_loan_amount': max_amount,
                    'interest_rate_range': f"{lender.get('interest_rate_min', 0)}% - {lender.get('interest_rate_max', 0)}%",
                    'amount_suitable': amount_suitable,
                    'latitude': lender_lat,
                    'longitude': lender_lon,
                    'regional_office': lender.get('city', 'Unknown'),
                    'classification': lender.get('type', 'NBFC'),
                    'suitability_score': self._calculate_suitability_score(lender, loan_request, distance)
                }
                
                recommendations.append(recommendation)
            
            final_recommendations = recommendations
            
            # Print search progress
            print(f"Search radius {radius}km: Found {len(recommendations)} lenders")
            
            if len(recommendations) >= min_lenders_required:
                break
        
        # Sort by distance first (closest first), then by suitability score
        final_recommendations.sort(key=lambda x: (x['distance_km'], -x['suitability_score']))
        
        # Ensure we return at least 10, or all available if less than 10
        recommended_count = max(min_lenders_required, len(final_recommendations))
        top_recommendations = final_recommendations[:recommended_count]
        
        # Generate map with all found lenders
        map_html = self._generate_map(user_lat, user_lon, top_recommendations, user_location)
        
        return {
            "user_location": user_location,
            "user_coordinates": [user_lat, user_lon],
            "total_lenders_found": len(final_recommendations),
            "recommendations": top_recommendations,
            "map_html": map_html,
            "search_criteria": {
                "loan_type": loan_type,
                "loan_amount": loan_amount,
                "final_search_radius_km": final_radius,
                "min_lenders_required": min_lenders_required
            }
        }
    
    def _extract_user_location(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Extract user location from profile data with comprehensive address hierarchy"""
        
        # Build comprehensive address from available fields (most specific to most general)
        address_parts = []
        
        # House number and street (most specific)
        house_number = user_data.get('house_number', '').strip()
        street = user_data.get('street', '').strip()
        if house_number and street:
            address_parts.append(f"{house_number}, {street}")
        elif street:
            address_parts.append(street)
        elif house_number:
            address_parts.append(house_number)
        
        # Landmark
        landmark = user_data.get('landmark', '').strip()
        if landmark:
            address_parts.append(f"Near {landmark}")
        
        # Village/Town name
        village = user_data.get('village_name', '').strip() or user_data.get('city', '').strip() or user_data.get('village', '').strip()
        if village:
            address_parts.append(village)
        
        # Taluk/Tehsil
        taluk = user_data.get('taluk', '').strip()
        if taluk:
            address_parts.append(f"{taluk} Taluk")
        
        # District
        district = user_data.get('district', '').strip()
        if district:
            address_parts.append(f"{district} District")
        
        # State 
        state = user_data.get('state', '').strip()
        if state:
            address_parts.append(state)
        else:
            # Auto-detect state based on district
            if district:
                karnataka_districts = ['bangalore', 'bengaluru', 'mysore', 'tumkur', 'mandya', 'hassan', 'davangere', 'shimoga', 'gulbarga', 'bijapur', 'belgaum', 'hubli', 'dharwad', 'bellary', 'raichur', 'bidar', 'chitradurga', 'kolar', 'chikmagalur', 'kodagu', 'udupi', 'dakshina kannada', 'uttara kannada']
                andhra_districts = ['nellore', 'guntur', 'krishna', 'west godavari', 'east godavari', 'visakhapatnam', 'vizianagaram', 'srikakulam', 'chittoor', 'cuddapah', 'anantapur', 'kurnool', 'prakasam', 'spsr nellore']
                
                district_lower = district.lower()
                if any(dist in district_lower for dist in karnataka_districts):
                    address_parts.append("Karnataka")
                elif any(dist in district_lower for dist in andhra_districts):
                    address_parts.append("Andhra Pradesh")
                else:
                    address_parts.append("Karnataka")  # Default to Karnataka
        
        # Pincode
        pincode = user_data.get('pincode', '').strip()
        if pincode:
            address_parts.append(pincode)
        
        # Always add India at the end
        address_parts.append("India")
        
        # Join with commas for final address
        if len(address_parts) > 1:  # More than just "India"
            full_address = ", ".join(address_parts)
            print(f"Constructed detailed address for geocoding: {full_address}")
            return full_address
        
        # Fallback to any available location field
        location_fields = ['village_name', 'district', 'city', 'location', 'village', 'taluk', 'address', 'police_station']
        
        for field in location_fields:
            value = user_data.get(field, '').strip()
            if value:
                fallback_address = f"{value}, Karnataka, India"
                print(f"Using fallback address from {field}: {fallback_address}")
                return fallback_address
        
        return None
    
    def _calculate_suitability_score(self, lender: pd.Series, loan_request: Dict[str, Any], distance: float) -> float:
        """Calculate suitability score for a lender (0-100)"""
        score = 50  # Base score
        
        # Distance factor (closer is better)
        if distance <= 10:
            score += 20
        elif distance <= 25:
            score += 15
        elif distance <= 50:
            score += 10
        elif distance <= 100:
            score += 5
        
        # Loan amount suitability
        loan_amount = loan_request.get('amount', 0)
        min_amount = lender.get('min_loan_amount', 0)
        max_amount = lender.get('max_loan_amount', float('inf'))
        
        if min_amount <= loan_amount <= max_amount:
            score += 20
        elif loan_amount < min_amount:
            score -= 10
        elif loan_amount > max_amount:
            score -= 15
        
        # Specialization match
        loan_type = loan_request.get('type', '').lower()
        specialization = str(lender.get('specialization', '')).lower()
        
        if loan_type in self.loan_type_mapping:
            keywords = self.loan_type_mapping[loan_type]
            if any(keyword in specialization for keyword in keywords):
                score += 15
        
        # Interest rate (lower is better)
        interest_min = lender.get('interest_rate_min', 20)
        if interest_min <= 12:
            score += 10
        elif interest_min <= 15:
            score += 5
        elif interest_min >= 20:
            score -= 5
        
        return min(100, max(0, score))
    
    def _generate_map(self, user_lat: float, user_lon: float, recommendations: List[Dict], user_location: str) -> str:
        """Generate HTML map with user location and lender recommendations"""
        try:
            # Create map centered on user location
            m = folium.Map(
                location=[user_lat, user_lon],
                zoom_start=10,
                tiles='OpenStreetMap'
            )
            
            # Add user location marker
            folium.Marker(
                [user_lat, user_lon],
                popup=f"<b>Your Location</b><br>{user_location}",
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
            
            # Add lender markers
            for i, lender in enumerate(recommendations):
                if lender.get('latitude') and lender.get('longitude'):
                    # Choose marker color based on suitability score
                    score = lender.get('suitability_score', 0)
                    if score >= 80:
                        color = 'green'
                    elif score >= 60:
                        color = 'orange'
                    else:
                        color = 'blue'
                    
                    popup_text = f"""
                    <b>{lender['name']}</b><br>
                    Type: {lender['type']}<br>
                    City: {lender['city']}<br>
                    Distance: {lender['distance_km']} km<br>
                    Specialization: {lender['specialization']}<br>
                    Interest Rate: {lender['interest_rate_range']}<br>
                    Loan Range: ₹{lender['min_loan_amount']:,} - ₹{lender['max_loan_amount']:,}<br>
                    Suitability Score: {score}/100
                    """
                    
                    folium.Marker(
                        [lender['latitude'], lender['longitude']],
                        popup=folium.Popup(popup_text, max_width=300),
                        icon=folium.Icon(color=color, icon='bank')
                    ).add_to(m)
            
            # Add legend
            legend_html = '''
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 150px; height: 90px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <b>Legend</b><br>
            <i class="fa fa-home" style="color:red"></i> Your Location<br>
            <i class="fa fa-bank" style="color:green"></i> High Suitability<br>
            <i class="fa fa-bank" style="color:orange"></i> Medium Suitability<br>
            <i class="fa fa-bank" style="color:blue"></i> Low Suitability
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            
            return m._repr_html_()
            
        except Exception as e:
            print(f"Error generating map: {e}")
            return f"<p>Error generating map: {e}</p>"
    
    def generate_lender_analysis(self, recommendations: List[Dict], loan_request: Dict[str, Any], language: str = "english") -> str:
        """Generate AI-powered analysis of lender recommendations"""
        
        if not recommendations:
            return "No suitable lenders found in your area. Please consider expanding your search radius or checking nearby districts."
        
        # Prepare data for AI analysis
        top_lenders = recommendations[:5]
        loan_amount = loan_request.get('amount', 0)
        loan_type = loan_request.get('type', 'personal')
        
        analysis_prompt = f"""
        Analyze these lender recommendations for a microfinance loan and provide helpful advice:

        Loan Request:
        - Amount: ₹{loan_amount:,}
        - Type: {loan_type}
        - Purpose: {loan_request.get('purpose', 'Not specified')}

        Top Recommended Lenders:
        {json.dumps(top_lenders, indent=2)}

        Provide a comprehensive analysis covering:
        1. Best lender options and why
        2. Interest rate comparison
        3. Distance vs. benefits trade-off
        4. Tips for loan application
        5. What documents to prepare
        6. Negotiation strategies

        Write in a helpful, advisory tone for rural microfinance customers.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial advisor specializing in rural microfinance in India. Provide practical, actionable advice."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content.strip()
            
            # Translate if needed
            if language != "english":
                analysis = self.translator.translate_response_to_user_language(
                    analysis, 
                    {"preferred_language": language}
                )
            
            return analysis
            
        except Exception as e:
            print(f"Error generating lender analysis: {e}")
            return "Unable to generate detailed analysis at this time. Please review the lender recommendations manually."
    
    def get_lender_contact_info(self, lender_name: str) -> Dict[str, Any]:
        """Get contact information for a specific lender"""
        lender_row = self.lender_data[self.lender_data['name'].str.contains(lender_name, case=False, na=False)]
        
        if lender_row.empty:
            return {"error": "Lender not found"}
        
        lender = lender_row.iloc[0]
        
        return {
            "name": lender.get('name', ''),
            "type": lender.get('type', ''),
            "city": lender.get('city', ''),
            "state": lender.get('state', ''),
            "phone": lender.get('phone', 'Contact information not available'),
            "email": lender.get('email', 'Email not available'),
            "website": lender.get('website', 'Website not available'),
            "address": lender.get('address', 'Address not available'),
            "specialization": lender.get('specialization', ''),
            "loan_range": f"₹{lender.get('min_loan_amount', 0):,} - ₹{lender.get('max_loan_amount', 0):,}",
            "interest_rates": f"{lender.get('interest_rate_min', 0)}% - {lender.get('interest_rate_max', 0)}%"
        }

# Example usage and testing
if __name__ == "__main__":
    agent = LenderRecommendationAgent()
    
    # Test with sample user data
    sample_user = {
        "village_name": "Davangere",
        "district": "Davangere",
        "state": "Karnataka"
    }
    
    sample_loan_request = {
        "amount": 50000,
        "type": "agriculture",
        "purpose": "crop cultivation"
    }
    
    # Test recommendation
    result = agent.recommend_lenders(sample_user, sample_loan_request)
    
    print("Lender Recommendations:")
    print(f"Found {result['total_lenders_found']} lenders")
    
    for i, lender in enumerate(result['recommendations'][:3], 1):
        print(f"\n{i}. {lender['name']}")
        print(f"   Distance: {lender['distance_km']} km")
        print(f"   Suitability Score: {lender['suitability_score']}/100")
        print(f"   Interest Rate: {lender['interest_rate_range']}")
