#!/usr/bin/env python3
"""
Quick Database Check - Verify API-Football Data
"""

import sqlite3
from datetime import datetime

def check_database_status():
    """Check current database status with API-Football data."""
    
    print("🔍 CHECKING DATABASE STATUS")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('data/football_betting.db')
        cursor = conn.cursor()
        
        # Check total matches
        cursor.execute('SELECT COUNT(*) FROM matches')
        total_matches = cursor.fetchone()[0]
        print(f"📊 Total matches in database: {total_matches}")
        
        # Check API-Football matches specifically
        cursor.execute('SELECT COUNT(*) FROM matches WHERE external_id IS NOT NULL')
        api_matches = cursor.fetchone()[0]
        print(f"🏆 API-Football matches: {api_matches}")
        
        # Check live matches
        cursor.execute('SELECT COUNT(*) FROM matches WHERE status = "Live"')
        live_matches = cursor.fetchone()[0]
        print(f"🔥 Live matches: {live_matches}")
        
        # Show recent API-Football matches
        cursor.execute('''
            SELECT home_team, away_team, status, competition, home_score, away_score, external_id
            FROM matches 
            WHERE external_id IS NOT NULL
            ORDER BY rowid DESC
            LIMIT 10
        ''')
        
        api_matches_data = cursor.fetchall()
        
        if api_matches_data:
            print(f"\n📋 Recent API-Football matches:")
            for match in api_matches_data:
                home_team, away_team, status, competition, home_score, away_score, external_id = match
                
                if status == "Live":
                    score_str = f"{home_score}-{away_score}" if home_score is not None else "0-0"
                    print(f"  🔥 LIVE: {home_team} {score_str} {away_team} ({competition}) [ID: {external_id}]")
                elif status == "Scheduled":
                    print(f"  📅 UPCOMING: {home_team} vs {away_team} ({competition}) [ID: {external_id}]")
                else:
                    score_str = f"{home_score}-{away_score}" if home_score is not None else "N/A"
                    print(f"  ✅ FINISHED: {home_team} {score_str} {away_team} ({competition}) [ID: {external_id}]")
        
        # Check teams count
        cursor.execute('SELECT COUNT(*) FROM teams')
        team_count = cursor.fetchone()[0]
        print(f"\n👥 Teams in database: {team_count}")
        
        # Check odds count
        cursor.execute('SELECT COUNT(*) FROM odds')
        odds_count = cursor.fetchone()[0]
        print(f"💰 Odds records: {odds_count}")
        
        conn.close()
        
        print(f"\n✅ Database check completed at {datetime.now().strftime('%H:%M:%S')}")
        
        # Status summary
        if api_matches > 0:
            print(f"\n🎉 SUCCESS: {api_matches} real API-Football matches loaded!")
            print("✅ Your GUI will now show real data instead of demo data")
            return True
        else:
            print(f"\n⚠️ No API-Football data found")
            print("❌ GUI will still show demo/sample data")
            return False
            
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def check_live_matches_for_predictions():
    """Check which matches will be used for enhanced predictions."""
    try:
        conn = sqlite3.connect('data/football_predictions.db')
        cursor = conn.cursor()
        
        print("🎯 LIVE MATCHES FOR ENHANCED PREDICTIONS")
        print("=" * 60)
        
        # Get matches with external_id (real API-Football matches)
        cursor.execute("""
            SELECT home_team, away_team, status, competition, match_date, external_id
            FROM matches 
            WHERE external_id IS NOT NULL
            ORDER BY match_date ASC
            LIMIT 10
        """)
        
        matches = cursor.fetchall()
        
        if matches:
            print(f"✅ Found {len(matches)} real live matches:")
            print()
            for i, match in enumerate(matches, 1):
                home_team = match[0] or "Unknown"
                away_team = match[1] or "Unknown"
                status = match[2] or "SCHEDULED"
                competition = match[3] or "League"
                match_date = match[4] or "Unknown"
                external_id = match[5]
                
                print(f"{i}. {home_team} vs {away_team}")
                print(f"   📅 Date: {match_date}")
                print(f"   🏆 Competition: {competition}")
                print(f"   🔗 API ID: {external_id}")
                print(f"   📊 Status: {status}")
                print()
        else:
            print("❌ No real matches found with external_id")
            print("Enhanced predictions will show demo data")
        
        # Also check total matches
        cursor.execute("SELECT COUNT(*) FROM matches")
        total_matches = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches WHERE external_id IS NOT NULL")
        real_matches = cursor.fetchone()[0]
        
        print(f"📊 SUMMARY:")
        print(f"   Total matches in database: {total_matches}")
        print(f"   Real API-Football matches: {real_matches}")
        print(f"   Demo matches: {total_matches - real_matches}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database_status()
    check_live_matches_for_predictions() 