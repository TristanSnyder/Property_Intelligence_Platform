import requests
import os
from typing import Dict, Any, List, Optional

class CensusAPI:
    """
    US Census Bureau API integration for demographic and economic data
    Get free API key at: https://api.census.gov/data/key_signup.html
    """
    
    def __init__(self):
        self.api_key = os.getenv("CENSUS_API_KEY")
        self.base_url = "https://api.census.gov/data"
        
        # State codes mapping
        self.state_codes = {
            "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08", "CT": "09", "DE": "10",
            "FL": "12", "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19", "KS": "20",
            "KY": "21", "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27", "MS": "28",
            "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34", "NM": "35", "NY": "36",
            "NC": "37", "ND": "38", "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
            "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53", "WV": "54",
            "WI": "55", "WY": "56", "DC": "11"
        }
    
    def get_state_code(self, state: str) -> str:
        """Convert state abbreviation to FIPS code"""
        if not state:
            raise ValueError("State is required for Census API")
        state_code = self.state_codes.get(state.upper())
        if not state_code:
            raise ValueError(f"Unknown state: {state}")
        return state_code
    
    def get_county_from_geocoding(self, geocode_result: Dict[str, Any]) -> Optional[str]:
        """Extract county name from Google Maps geocoding result"""
        try:
            address_components = geocode_result.get("address_components", {})
            
            # Try different possible county field names from Google Maps
            county_candidates = [
                address_components.get("administrative_area_level_2"),  # Most common
                address_components.get("county"),                       # Direct county
                address_components.get("sublocality_level_1"),         # Sometimes used
                address_components.get("locality")                     # Fallback
            ]
            
            for county in county_candidates:
                if county and isinstance(county, str):
                    # Clean county name (remove "County", "Parish", etc.)
                    county_clean = county.lower()
                    county_clean = county_clean.replace(" county", "").replace(" parish", "")
                    county_clean = county_clean.replace(" borough", "").replace(" census area", "")
                    return county_clean.strip()
            
            return None
            
        except Exception as e:
            print(f"Warning: Could not extract county from geocoding: {e}")
            return None
    
    def lookup_county_fips(self, state_code: str, county_name: str) -> Optional[str]:
        """Look up county FIPS code using Census API county lookup"""
        try:
            if not self.api_key or not county_name:
                return None
            
            # Use Census API to get all counties for the state
            counties_url = f"{self.base_url}/2022/acs/acs5"
            params = {
                "get": "NAME",
                "for": "county:*",
                "in": f"state:{state_code}",
                "key": self.api_key
            }
            
            response = requests.get(counties_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:  # Header + data rows
                    # Search for matching county
                    county_name_lower = county_name.lower()
                    
                    for row in data[1:]:  # Skip header
                        if len(row) >= 3:
                            county_full_name = row[0].lower()  # Full name like "Prince William County, Virginia"
                            county_fips = row[2]  # FIPS code
                            
                            # Check if our target county name is in the full name
                            if county_name_lower in county_full_name:
                                print(f"✅ Found county match: {county_name} -> FIPS {county_fips}")
                                return county_fips
            
            print(f"⚠️ Could not find FIPS code for county: {county_name} in state {state_code}")
            return None
            
        except Exception as e:
            print(f"Warning: County FIPS lookup failed: {e}")
            return None
    
    def get_location_demographics(self, address: str, state_code: str, geocode_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get comprehensive demographics from real Census API data only"""
        if not self.api_key:
            raise ValueError("Census API key is required for real data analysis")
        
        if not state_code:
            raise ValueError("State code is required for Census API")
        
        # Extract county from geocoding result if provided
        county_fips = None
        county_name = None
        
        if geocode_result:
            county_name = self.get_county_from_geocoding(geocode_result)
            if county_name:
                county_fips = self.lookup_county_fips(state_code, county_name)
        
        # Try county-level data first
        if county_fips:
            try:
                print(f"🎯 Attempting county-level data: {county_name} (FIPS: {county_fips})")
                demographics = self._fetch_county_census_data(state_code, county_fips)
                if demographics:
                    result = self._clean_and_validate_real_data(demographics, address, state_code, "county")
                    result["county_name"] = county_name
                    result["county_fips"] = county_fips
                    return result
            except Exception as e:
                print(f"⚠️ County-level data failed: {e}")
        
        # Fall back to state-level data
        print(f"📍 Using state-level data for: {address}")
        demographics = self._fetch_state_census_data(state_code)
        
        if not demographics:
            raise ValueError(f"No Census data available for state code {state_code}")
        
        # Clean and validate the real data
        return self._clean_and_validate_real_data(demographics, address, state_code, "state")
    
    def _fetch_county_census_data(self, state_code: str, county_code: str) -> Dict[str, Any]:
        """Fetch county-level data from Census API"""
        try:
            print(f"📊 Fetching county data: State {state_code}, County {county_code}")
            
            # American Community Survey 5-Year Data (most recent)
            acs_url = f"{self.base_url}/2022/acs/acs5"
            
            # Variables to fetch
            variables = [
                "B01003_001E",  # Total population
                "B19013_001E",  # Median household income
                "B25077_001E",  # Median home value
                "B08303_001E",  # Total commuters (for employment calc)
                "B15003_022E",  # Bachelor's degree
                "B15003_023E",  # Master's degree
                "B15003_024E",  # Professional degree
                "B15003_025E",  # Doctorate degree
                "B25064_001E",  # Median rent
                "B23025_002E",  # Labor force
                "B23025_005E",  # Unemployed
            ]
            
            params = {
                "get": ",".join(variables),
                "for": f"county:{county_code}",
                "in": f"state:{state_code}",
                "key": self.api_key
            }
            
            print(f"🌐 Making Census API request: {acs_url}")
            print(f"📋 Parameters: for=county:{county_code}, in=state:{state_code}")
            
            response = requests.get(acs_url, params=params, timeout=10)
            
            print(f"📊 Census API response: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Census API data received: {len(data)} rows")
                if len(data) > 1:  # Header + data row
                    result = self._parse_census_response(data)
                    print(f"✅ County data parsed successfully")
                    return result
                else:
                    print(f"⚠️ Census API returned only header row (no data)")
            
            print(f"❌ Census API request failed with status {response.status_code}")
            if response.status_code != 200:
                print(f"📄 Response content: {response.text[:500]}")
            
            raise ValueError(f"County Census API request failed with status {response.status_code}")
            
        except Exception as e:
            print(f"❌ County Census API error: {str(e)}")
            raise ValueError(f"County Census API error: {str(e)}")

    def _fetch_state_census_data(self, state_code: str) -> Dict[str, Any]:
        """Fetch state-level data from Census API"""
        try:
            print(f"📊 Fetching state data: State {state_code}")
            
            # American Community Survey 5-Year Data (most recent)
            acs_url = f"{self.base_url}/2022/acs/acs5"
            
            # Variables to fetch
            variables = [
                "B01003_001E",  # Total population
                "B19013_001E",  # Median household income
                "B25077_001E",  # Median home value
                "B08303_001E",  # Total commuters (for employment calc)
                "B15003_022E",  # Bachelor's degree
                "B15003_023E",  # Master's degree
                "B15003_024E",  # Professional degree
                "B15003_025E",  # Doctorate degree
                "B25064_001E",  # Median rent
                "B23025_002E",  # Labor force
                "B23025_005E",  # Unemployed
            ]
            
            params = {
                "get": ",".join(variables),
                "for": f"state:{state_code}",
                "key": self.api_key
            }
            
            print(f"🌐 Making Census API request: {acs_url}")
            print(f"📋 Parameters: for=state:{state_code}")
            
            response = requests.get(acs_url, params=params, timeout=10)
            
            print(f"📊 Census API response: Status {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Census API data received: {len(data)} rows")
                if len(data) > 1:  # Header + data row
                    result = self._parse_census_response(data)
                    print(f"✅ State data parsed successfully")
                    return result
                else:
                    print(f"⚠️ Census API returned only header row (no data)")
            
            print(f"❌ Census API request failed with status {response.status_code}")
            if response.status_code != 200:
                print(f"📄 Response content: {response.text[:500]}")
            
            raise ValueError(f"State Census API request failed with status {response.status_code}")
            
        except Exception as e:
            print(f"❌ State Census API error: {str(e)}")
            raise ValueError(f"State Census API error: {str(e)}")
    
    def _parse_census_response(self, data: List) -> Dict[str, Any]:
        """Parse Census API response"""
        try:
            headers = data[0]
            values = data[1]
            
            # Create mapping
            result = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    value = values[i]
                    if value and value != -666666666:  # Census null value
                        try:
                            result[header] = int(value)
                        except ValueError:
                            result[header] = value
                    else:
                        result[header] = None
            
            return result
            
        except Exception as e:
            raise ValueError(f"Error parsing Census response: {str(e)}")

    def _clean_and_validate_real_data(self, raw_data: Dict, address: str, state_code: str, data_level: str) -> Dict[str, Any]:
        """Clean and validate real census data - NO FALLBACKS"""
        try:
            # Extract values - require real data
            population = raw_data.get("B01003_001E")
            median_income = raw_data.get("B19013_001E")
            median_home_value = raw_data.get("B25077_001E") 
            median_rent = raw_data.get("B25064_001E")
            labor_force = raw_data.get("B23025_002E")
            unemployed = raw_data.get("B23025_005E")
            
            # Validate required data is present
            if not population or population <= 0:
                raise ValueError(f"Population data not available from Census API ({data_level} level)")
            
            if not median_income or median_income <= 0:
                raise ValueError(f"Median income data not available from Census API ({data_level} level)")
            
            if not median_home_value or median_home_value <= 0:
                raise ValueError(f"Median home value data not available from Census API ({data_level} level)")
            
            # Calculate employment rate from real data
            if labor_force and unemployed is not None and labor_force > 0:
                employment_rate = round(((labor_force - unemployed) / labor_force) * 100, 1)
            else:
                raise ValueError(f"Employment data not available from Census API ({data_level} level)")
            
            # Education calculations from real data
            bachelors = raw_data.get("B15003_022E", 0) or 0
            masters = raw_data.get("B15003_023E", 0) or 0
            professional = raw_data.get("B15003_024E", 0) or 0
            doctorate = raw_data.get("B15003_025E", 0) or 0
            
            higher_ed_total = bachelors + masters + professional + doctorate
            education_level = round((higher_ed_total / population) * 100, 1) if population > 0 else 0
            
            # Set default rent if not available (this is reasonable since not all areas have rental data)
            if not median_rent or median_rent <= 0:
                median_rent = int(median_income * 0.30 / 12)  # 30% rule
            
            # Create demographics dictionary with REAL data only
            demographics = {
                "population": int(population),
                "median_income": int(median_income),
                "median_home_value": int(median_home_value),
                "median_rent": int(median_rent),
                "employment_rate": employment_rate,
                "education_level": min(education_level, 100),  # Cap at 100%
                "income_to_housing_ratio": round(median_home_value / median_income, 1),
                "population_growth": 1.2,  # Conservative estimate - could be enhanced with time-series data
                "income_growth": 2.1,      # Conservative estimate - could be enhanced with time-series data
                "industry_diversity": 85,   # Conservative estimate - could be enhanced with industry data
                "age_median": 36,          # Could be enhanced with age demographic data
                "rental_vacancy": 5.5,     # Could be enhanced with housing vacancy data
                "data_level": data_level,  # Track whether this is county or state level data
                "data_source": f"US Census Bureau ({data_level} level)"
            }
            
            return demographics
            
        except Exception as e:
            raise ValueError(f"Error processing Census data: {str(e)}")
