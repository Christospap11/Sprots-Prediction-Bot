"""
Simple API Key Test for API-Football
Tests the API key and provides troubleshooting steps
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_football_key():
    """Test API-Football key and provide troubleshooting"""
    print("🔑 Testing API-Football Key...")
    print("=" * 50)
    
    api_key = os.getenv("API_FOOTBALL_KEY")
    
    if not api_key:
        print("❌ No API key found in .env file")
        print("💡 Make sure your .env file contains: API_FOOTBALL_KEY=your_key_here")
        return False
    
    print(f"🔍 Using API key: {api_key[:10]}...{api_key[-4:]}")
    
    # Test with a simple endpoint
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }
    
    # Try the timezone endpoint (simplest test)
    url = "https://api-football-v1.p.rapidapi.com/v3/timezone"
    
    try:
        print("🧪 Testing API connection...")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API key is working!")
            print(f"📈 Found {len(data.get('response', []))} timezones")
            
            # Test a more complex endpoint
            print("\n🔄 Testing leagues endpoint...")
            leagues_url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
            params = {"current": "true"}
            
            leagues_response = requests.get(leagues_url, headers=headers, params=params, timeout=10)
            
            if leagues_response.status_code == 200:
                leagues_data = leagues_response.json()
                league_count = len(leagues_data.get('response', []))
                print(f"✅ Leagues endpoint working! Found {league_count} current leagues")
                
                # Show some example leagues
                if leagues_data.get('response'):
                    print("\n🏆 Sample leagues available:")
                    for league in leagues_data['response'][:5]:
                        league_info = league.get('league', {})
                        country = league.get('country', {}).get('name', 'Unknown')
                        print(f"   • {league_info.get('name', 'Unknown')} ({country})")
                
                return True
            else:
                print(f"⚠️ Leagues endpoint failed: {leagues_response.status_code}")
                print(f"Response: {leagues_response.text[:200]}...")
                
        elif response.status_code == 403:
            print("❌ 403 Forbidden - API key issues")
            print("\n🔧 Troubleshooting Steps:")
            print("1. 🌐 Go to: https://rapidapi.com/api-sports/api/api-football/")
            print("2. 📝 Make sure you're logged into RapidAPI")
            print("3. 🔄 Subscribe to API-Football (free tier available)")
            print("4. ✅ Verify your subscription is active")
            print("5. 🔑 Copy the correct API key from your RapidAPI dashboard")
            print("6. 📁 Update your .env file with the new key")
            
        elif response.status_code == 429:
            print("❌ 429 Too Many Requests - Rate limit exceeded")
            print("💡 Wait a few minutes and try again")
            
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        print("🌐 Check your internet connection")
        
    return False

def show_next_steps():
    """Show next steps based on API test results"""
    print("\n🚀 Next Steps After API Setup:")
    print("=" * 40)
    print("1. ✅ Ensure API key is working (run this test again)")
    print("2. 🔄 Start enhanced data collection:")
    print("   python -c \"from src.data_collectors.statistics_collector import run_statistics_collector; import asyncio; asyncio.run(run_statistics_collector())\"")
    print("3. 🎮 Launch your enhanced GUI:")
    print("   python launch_app.py")
    print("4. 📈 Watch your prediction accuracy improve!")
    
    print("\n💰 API-Football Pricing:")
    print("   🆓 Free: 100 requests/day (great for testing)")
    print("   💪 Pro: $19/month - 7,500 requests/day (recommended)")
    print("   🚀 Ultra: $29/month - 75,000 requests/day")
    
    print("\n📚 More Information:")
    print("   📖 Full API guide: STATISTICS_APIS_GUIDE.md")
    print("   🧪 Test all APIs: python test_statistics_apis.py")
    print("   ⚙️ Setup help: python setup_statistics_apis.py")

if __name__ == "__main__":
    print("🔥 API-Football Key Verification Tool")
    print("="*50)
    
    success = test_api_football_key()
    
    if success:
        print("\n🎉 SUCCESS! Your API key is working perfectly!")
        print("🚀 You're ready to collect enhanced statistics!")
    else:
        print("\n🔧 API key needs attention - follow the troubleshooting steps above")
    
    show_next_steps() 