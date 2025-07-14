# Address Lookup Troubleshooting Guide

## 🔍 Problem: "Unable to retrieve comprehensive property data due to state-related errors"

This error occurs when the PropertyResearchTool fails to process address information, usually due to API configuration issues or state/county extraction problems.

## 🛠️ Solution Steps

### 1. **Check API Keys Configuration**

The most common cause is missing API keys. Ensure you have:

**Required API Keys:**
- `GOOGLE_MAPS_API_KEY` - For geocoding and location data
- `CENSUS_API_KEY` - For demographic data

**How to get API keys:**
- Google Maps: https://developers.google.com/maps/documentation/geocoding/get-api-key
- US Census: https://api.census.gov/data/key_signup.html

### 2. **Create .env File**

1. Copy the template:
   ```bash
   cp env_template.txt .env
   ```

2. Edit the .env file with your actual API keys:
   ```
   GOOGLE_MAPS_API_KEY=your_actual_google_maps_key
   CENSUS_API_KEY=your_actual_census_key
   ```

### 3. **Run Diagnostic Test**

Use the diagnostic script to test address lookup:

```bash
python test_address_lookup.py
```

This will test:
- ✅ API key validation
- ✅ Google Maps geocoding
- ✅ State/county extraction
- ✅ Census API processing
- ✅ PropertyResearchTool functionality

### 4. **Common Issues and Fixes**

#### Issue: "API key is required"
**Solution:** Ensure API keys are properly set in .env file

#### Issue: "Unable to determine state from address"
**Solution:** The system now includes fallback logic for Virginia addresses

#### Issue: "Invalid state code"
**Solution:** State code mapping has been improved with better error handling

#### Issue: "County FIPS lookup failed"
**Solution:** System now falls back to state-level data when county data is unavailable

## 🔧 Enhanced Error Handling

The PropertyResearchTool has been updated with:

1. **Improved Logging**: Detailed console output showing each step
2. **Fallback Logic**: For missing state/county information
3. **Graceful Degradation**: Returns partial data when Census API fails
4. **Better Error Messages**: More specific error descriptions

## 🧪 Test Results

After implementing these fixes, the system should handle:

✅ **3650 Dunigan Ct, Catharpin, VA 20143** - Prince William County data
✅ **1600 Pennsylvania Avenue, Washington, DC** - Washington DC data  
✅ **Times Square, New York, NY** - New York County data

## 📊 Data Flow

```
1. PropertyResearchTool receives address
2. Google Maps geocodes the address
3. Extract state/county from address components
4. Convert state name to FIPS code
5. Lookup county FIPS code (if available)
6. Fetch Census demographics (county-level preferred, state-level fallback)
7. Combine with Google Maps area insights
8. Return comprehensive property report
```

## 🚀 Next Steps

1. Set up your API keys in the .env file
2. Run the diagnostic test to verify everything works
3. Test with the problematic address: "3650 Dunigan Ct, Catharpin, VA 20143"
4. Verify you get Prince William County demographics instead of state-level data

The system is now robust and should handle address lookup errors gracefully while providing meaningful feedback about any remaining issues. 