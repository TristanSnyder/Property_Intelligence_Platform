import requests
import os
from typing import Dict, Any, Optional
import json

class CensusAPI:
    """
    US Census Bureau API integration for demographic and economic data
    Free API - get key at: https://api.census.gov/data/key_signup.html
    """
    
    def __init__(self):
        self.api_key = os.getenv("CENSUS_API_KEY")
        self.base_url = "https://api.census.gov/data"
        
    def get_location_demographics(self, address: str, state_code: str = None, county_code: str = None) -> Dict[str, Any]:
        """Get demographic data for a location"""
        try:
            # Use American Community Survey 5-Year Data (most comprehensive)
            year = "2022"  # Latest available
            dataset = f"{year}/acs/acs5"
            
            # Key demographic variables
            variables = [
                "NAME",  # Geographic name
                "B01003_001E",  # Total population
                "B25077_001E",  # Median home value
                "B19013_001E",  # Median household income
                "B25001_001E",  # Total housing units
                "B25003_002E",  # Owner-occupied housing units
                "B25003_003E",  # Renter-occupied housing units
                "B08303_001E",  # Total commuters
                "B08303_013E",  # Public transportation commuters
                "B15003_022E",  # Bachelor's degree
                "B15003_023E",  # Master's degree
                "B15003_024E",  # Professional degree
                "B15003_025E",  # Doctorate degree
                "B08013_001E",  # Aggregate travel time to work
                "B25064_001E",  # Median gross rent
            ]
            
            # Build API request
            params = {
                "get": ",".join(variables),
                "for": "county:*" if not county_code else f"county:{county_code}",
                "in": f"state:{state_code}" if state_code else "state:*",
                "key": self.api_key
            }
            
            if not self.api_key:
                return self._get_mock_demographics(address)
            
            response = requests.get(f"{self.base_url}/{dataset}", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 1:  # Skip header row
                    row = data[1]  # Take first data row
                    
                    # Parse the data
                    total_pop = self._safe_int(row[1])
                    median_home_value = self._safe_int(row[2])
                    median_income = self._safe_int(row[3])
                    total_housing = self._safe_int(row[4])
                    owner_occupied = self._safe_int(row[5])
                    renter_occupied = self._safe_int(row[6])
                    total_commuters = self._safe_int(row[7])
                    public_transit = self._safe_int(row[8])
                    bachelors = self._safe_int(row[9])
                    masters = self._safe_int(row[10])
                    professional = self._safe_int(row[11])
                    doctorate = self._safe_int(row[12])
                    avg_commute = self._safe_int(row[13])
                    median_rent = self._safe_int(row[14])
                    
                    # Calculate derived metrics
                    education_total = bachelors + masters + professional + doctorate
                    education_rate = (education_total / total_pop * 100) if total_pop > 0 else 0
                    homeownership_rate = (owner_occupied / (owner_occupied + renter_occupied) * 100) if (owner_occupied + renter_occupied) > 0 else 0
                    transit_rate = (public_transit / total_commuters * 100) if total_commuters > 0 else 0
                    avg_commute_minutes = (avg_commute / total_commuters) if total_commuters > 0 else 0
                    
                    return {
                        "location": address,
                        "data_source": "US Census Bureau API",
                        "year": year,
                        "population": {
                            "total": total_pop,
                            "density_category": self._get_density_category(total_pop)
                        },
                        "housing": {
                            "median_home_value": median_home_value,
                            "median_rent": median_rent,
                            "total_units": total_housing,
                            "homeownership_rate": round(homeownership_rate, 1)
                        },
                        "economics": {
                            "median_household_income": median_income,
                            "income_category": self._get_income_category(median_income)
                        },
                        "education": {
                            "bachelor_plus_rate": round(education_rate, 1),
                            "education_level": self._get_education_level(education_rate)
                        },
                        "transportation": {
                            "avg_commute_minutes": round(avg_commute_minutes, 1),
                            "public_transit_rate": round(transit_rate, 1),
                            "commute_category": self._get_commute_category(avg_commute_minutes)
                        }
                    }
            
            return self._get_mock_demographics(address)
            
        except Exception as e:
            print(f"Census API error: {str(e)}")
            return self._get_mock_demographics(address)
    
    def get_state_code(self, state_name: str) -> Optional[str]:
        """Convert state name to FIPS code"""
        state_codes = {
            "alabama": "01", "alaska": "02", "arizona": "04", "arkansas": "05",
            "california": "06", "colorado": "08", "connecticut": "09", "delaware": "10",
            "florida": "12", "georgia": "13", "hawaii": "15", "idaho": "16",
            "illinois": "17", "indiana": "18", "iowa": "19", "kansas": "20",
            "kentucky": "21", "louisiana": "22", "maine": "23", "maryland": "24",
            "massachusetts": "25", "michigan": "26", "minnesota": "27", "mississippi": "28",
            "missouri": "29", "montana": "30", "nebraska": "31", "nevada": "32",
            "new hampshire": "33", "new jersey": "34", "new mexico": "35", "new york": "36",
            "north carolina": "37", "north dakota": "38", "ohio": "39", "oklahoma": "40",
            "oregon": "41", "pennsylvania": "42", "rhode island": "44", "south carolina": "45",
            "south dakota": "46", "tennessee": "47", "texas": "48", "utah": "49",
            "vermont": "50", "virginia": "51", "washington": "53", "west virginia": "54",
            "wisconsin": "55", "wyoming": "56"
        }
        return state_codes.get(state_name.lower())
    
    def _safe_int(self, value) -> int:
        """Safely convert value to int"""
        try:
            if value is None or value == "null" or value == "":
                return 0
            return int(float(value))
        except:
            return 0
    
    def _get_density_category(self, population: int) -> str:
        """Categorize population density"""
        if population > 500000:
            return "High Density Urban"
        elif population > 100000:
            return "Urban"
        elif population > 50000:
            return "Suburban"
        else:
            return "Rural/Small Town"
    
    def _get_income_category(self, income: int) -> str:
        """Categorize income level"""
        if income > 100000:
            return "High Income"
        elif income > 75000:
            return "Upper Middle Income"
        elif income > 50000:
            return "Middle Income"
        elif income > 35000:
            return "Lower Middle Income"
        else:
            return "Lower Income"
    
    def _get_education_level(self, rate: float) -> str:
        """Categorize education level"""
        if rate > 50:
            return "Highly Educated"
        elif rate > 35:
            return "Well Educated"
        elif rate > 25:
            return "Moderately Educated"
        else:
            return "Lower Education"
    
    def _get_commute_category(self, minutes: float) -> str:
        """Categorize commute time"""
        if minutes > 35:
            return "Long Commute"
        elif minutes > 25:
            return "Moderate Commute"
        else:
            return "Short Commute"
    
    def _get_mock_demographics(self, address: str) -> Dict[str, Any]:
        """Fallback mock data when API is unavailable"""
        return {
            "location": address,
            "data_source": "Mock Data (Census API key not configured)",
            "year": "2022",
            "population": {
                "total": 45672,
                "density_category": "Suburban"
            },
            "housing": {
                "median_home_value": 385000,
                "median_rent": 1850,
                "total_units": 18450,
                "homeownership_rate": 68.9
            },
            "economics": {
                "median_household_income": 68500,
                "income_category": "Upper Middle Income"
            },
            "education": {
                "bachelor_plus_rate": 42.1,
                "education_level": "Well Educated"
            },
            "transportation": {
                "avg_commute_minutes": 28.5,
                "public_transit_rate": 12.3,
                "commute_category": "Moderate Commute"
            }
        }
