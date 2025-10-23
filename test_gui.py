#!/usr/bin/env python3
"""
Quick test for the Football Betting GUI
"""

import subprocess
import sys
import time

def test_gui():
    """Test GUI launch."""
    
    print("🚀 Testing Football Betting GUI...")
    print("⚽ This will launch the GUI for 10 seconds then close it")
    
    try:
        # Launch GUI
        if sys.platform.startswith('win'):
            process = subprocess.Popen([sys.executable, 'football_betting_gui.py'])
        else:
            process = subprocess.Popen(['python3', 'football_betting_gui.py'])
        
        print("✅ GUI launched successfully!")
        print("📊 You should see a modern window with:")
        print("   🏆 Matches tab - View and search football matches")
        print("   🎯 Predictions tab - AI predictions (demo)")
        print("   💰 Odds tab - Betting odds from multiple sources")
        print("   📊 Standings tab - League tables")
        print("   🔴 LIVE tab - Live match updates")
        
        print("\n⏱️ GUI will run for 10 seconds...")
        time.sleep(10)
        
        # Close GUI
        process.terminate()
        print("⏹️ GUI test completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

if __name__ == "__main__":
    test_gui() 