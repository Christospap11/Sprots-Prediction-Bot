#!/usr/bin/env python3
"""
System Check Script
Verify all system components are working properly
"""

def check_dependencies():
    """Check all required dependencies."""
    
    print("SYSTEM DEPENDENCY CHECK")
    print("=" * 40)
    
    dependencies = [
        ('sqlite3', 'Database support'),
        ('requests', 'HTTP requests'),
        ('pandas', 'Data analysis'),
        ('numpy', 'Numerical computing'),
        ('schedule', 'Task scheduling'),
        ('asyncio', 'Async support'),
        ('dotenv', 'Environment variables'),
    ]
    
    failed = []
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"OK: {module:12} - {description}")
        except ImportError:
            print(f"FAIL: {module:12} - {description}")
            failed.append(module)
    
    print(f"\nResult: {len(dependencies) - len(failed)}/{len(dependencies)} dependencies available")
    
    if failed:
        print(f"Missing: {', '.join(failed)}")
        return False
    
    return True


def check_project_structure():
    """Check project structure."""
    
    print("\nPROJECT STRUCTURE CHECK")
    print("=" * 40)
    
    import os
    from pathlib import Path
    
    required_paths = [
        'src/',
        'src/data/',
        'src/data/collectors/',
        'config/',
        'data/',
        'logs/',
        '.env',
        'requirements.txt'
    ]
    
    missing = []
    
    for path in required_paths:
        if os.path.exists(path):
            print(f"OK: {path}")
        else:
            print(f"MISSING: {path}")
            missing.append(path)
    
    print(f"\nResult: {len(required_paths) - len(missing)}/{len(required_paths)} paths found")
    
    if missing:
        print(f"Missing: {', '.join(missing)}")
        return False
    
    return True


def check_configuration():
    """Check configuration loading."""
    
    print("\nCONFIGURATION CHECK")
    print("=" * 40)
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from dotenv import load_dotenv
        load_dotenv()
        
        import os
        
        # Check environment variables
        env_vars = [
            'FOOTBALL_API_KEY',
            'ODDS_API_KEY', 
            'WEATHER_API_KEY'
        ]
        
        configured = 0
        for var in env_vars:
            value = os.getenv(var, '')
            if value and value != f"your_actual_{var.lower()}_here":
                print(f"OK: {var} - Configured")
                configured += 1
            else:
                print(f"NOT SET: {var} - Need to add to .env file")
        
        print(f"\nResult: {configured}/{len(env_vars)} API keys configured")
        
                 # Check database
        try:
            from config.settings import settings
            print(f"OK: Settings loaded successfully")
            print(f"OK: Database URL: {settings.database_url}")
            print(f"OK: Leagues configured: {len(settings.leagues_list)}")
            return True
        except Exception as e:
            print(f"FAIL: Settings loading error: {e}")
            return False
            
    except Exception as e:
        print(f"FAIL: Configuration error: {e}")
        return False


def check_database():
    """Check database connectivity."""
    
    print("\nDATABASE CHECK")
    print("=" * 40)
    
    try:
        import sqlite3
        import os
        
        db_path = "data/football_betting.db"
        
        if os.path.exists(db_path):
            print(f"OK: Database file exists: {db_path}")
            
            # Check database size
            size = os.path.getsize(db_path)
            print(f"OK: Database size: {size:,} bytes")
            
            # Test connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"OK: Database tables: {len(tables)}")
            for table in tables:
                print(f"    - {table[0]}")
            
            conn.close()
            return True
        else:
            print(f"INFO: Database not created yet: {db_path}")
            print("This is normal for first run - will be created automatically")
            return True
            
    except Exception as e:
        print(f"FAIL: Database error: {e}")
        return False


def check_scripts():
    """Check main scripts."""
    
    print("\nSCRIPT CHECK")
    print("=" * 40)
    
    scripts = [
        'simple_api_test.py',
        'run_realtime_monitor.py',
        'src/data/collectors/realtime_european_collector.py'
    ]
    
    import os
    
    all_good = True
    
    for script in scripts:
        if os.path.exists(script):
            print(f"OK: {script}")
        else:
            print(f"MISSING: {script}")
            all_good = False
    
    return all_good


def main():
    """Run all system checks."""
    
    print("SPORTS PREDICT BOT - SYSTEM CHECK")
    print("=" * 50)
    print("")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Configuration", check_configuration),
        ("Database", check_database),
        ("Scripts", check_scripts)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
            print("")
        except Exception as e:
            print(f"ERROR in {name}: {e}")
            results.append((name, False))
            print("")
    
    # Summary
    print("SUMMARY")
    print("=" * 20)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name:20} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\nSYSTEM STATUS: READY!")
        print("Next steps:")
        print("1. Add your API keys to .env file")
        print("2. Run: python simple_api_test.py")
        print("3. Run: python run_realtime_monitor.py")
    else:
        print("\nSYSTEM STATUS: NEEDS ATTENTION")
        print("Please fix the failed checks above")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"System check error: {e}")
        exit(1) 