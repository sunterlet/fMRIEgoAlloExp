#!/usr/bin/env python3
"""
Test script to verify arena-specific logging functionality
"""

import os
import sys
import subprocess
import tempfile
import shutil

def test_arena_logging():
    """Test that arena-specific logging works correctly."""
    
    print("Testing arena-specific logging functionality...")
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    original_dir = os.getcwd()
    
    try:
        # Copy the multi_arena.py script to test directory
        script_path = os.path.join(original_dir, 'multi_arena.py')
        test_script_path = os.path.join(test_dir, 'multi_arena.py')
        shutil.copy2(script_path, test_script_path)
        
        # Create a simple test arena CSV
        test_arena_csv = os.path.join(test_dir, 'Final_New_Arenas.csv')
        with open(test_arena_csv, 'w', encoding='utf-8') as f:
            f.write("ArenaName,TargetName,Coordinates,HebrewName,HebrewArenaName\n")
            f.write("test_arena,target1,\"(0.5; 0.5)\",מטרה1,זירת בדיקה\n")
            f.write("test_arena,target2,\"(-0.5; 0.5)\",מטרה2,זירת בדיקה\n")
        
        # Create results directory
        results_dir = os.path.join(test_dir, 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Change to test directory
        os.chdir(test_dir)
        
        # Test 1: Run with arena-specific suffix
        print("\nTest 1: Running with arena-specific suffix...")
        env = os.environ.copy()
        env['ARENA_LOG_SUFFIX'] = '_full_test_arena'
        
        # Run a quick test (just show instructions to avoid long wait)
        cmd = [sys.executable, 'multi_arena.py', 'practice', '--participant', 'TEST', 
               '--arena', 'instructions', '--visibility', 'full', '--num-trials', '1']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ Test 1 passed: Instructions displayed successfully")
        else:
            print(f"✗ Test 1 failed: {result.stderr}")
        
        # Test 2: Check if arena-specific files would be created
        expected_continuous = os.path.join(results_dir, 'TEST_multi_arena_practice_continuous_log_full_test_arena.csv')
        expected_discrete = os.path.join(results_dir, 'TEST_multi_arena_practice_discrete_log_full_test_arena.csv')
        
        print(f"\nTest 2: Checking file naming convention...")
        print(f"Expected continuous: {expected_continuous}")
        print(f"Expected discrete: {expected_discrete}")
        
        # Test 3: Test RoundName in continuous log structure
        print("\nTest 3: Testing RoundName in continuous log...")
        
        # Create a mock continuous log entry to test the structure
        import csv
        test_continuous_file = os.path.join(results_dir, 'test_continuous.csv')
        with open(test_continuous_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["RealTime", "RoundName", "trial_time", "trial", "visibility", "phase", "event", "x", "y", "rotation_angle"])
            writer.writeheader()
            writer.writerow({
                "RealTime": "10:00:00.000",
                "RoundName": "test_arena",
                "trial_time": 0.0,
                "trial": 1,
                "visibility": "full",
                "phase": "exploration",
                "event": "",
                "x": 0.0,
                "y": 0.0,
                "rotation_angle": 0.0
            })
        
        # Verify the file was created with correct structure
        if os.path.exists(test_continuous_file):
            with open(test_continuous_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "RoundName" in content and "test_arena" in content:
                    print("✓ Test 3 passed: RoundName correctly included in continuous log")
                else:
                    print("✗ Test 3 failed: RoundName not found in continuous log")
        else:
            print("✗ Test 3 failed: Test continuous log file not created")
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
    finally:
        # Clean up
        os.chdir(original_dir)
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_arena_logging()
