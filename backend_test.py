#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Advanced Calculator
Tests all endpoints: health, calculate, convert-number, financial-calculation, history
"""

import requests
import json
import time
import uuid
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = "http://localhost:8001"  # Will be updated from frontend/.env

def load_backend_url():
    """Load backend URL from frontend/.env file"""
    global BACKEND_URL
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    BACKEND_URL = line.split('=', 1)[1].strip()
                    break
        print(f"Using backend URL: {BACKEND_URL}")
    except Exception as e:
        print(f"Warning: Could not load backend URL from .env: {e}")
        print(f"Using default: {BACKEND_URL}")

class CalculatorAPITester:
    def __init__(self):
        load_backend_url()
        self.base_url = BACKEND_URL
        self.api_url = f"{self.base_url}/api"
        self.session_id = str(uuid.uuid4())
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_health_endpoint(self):
        """Test GET /api/health"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, f"Response: {data}")
                else:
                    self.log_test("Health Check", False, f"Unexpected response: {data}")
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")

    def test_basic_calculations(self):
        """Test basic arithmetic calculations"""
        test_cases = [
            {"expression": "2+2", "expected": 4},
            {"expression": "10*5", "expected": 50},
            {"expression": "15/3", "expected": 5},
            {"expression": "100-25", "expected": 75},
            {"expression": "2**3", "expected": 8},  # Power operation
            {"expression": "(10+5)*2", "expected": 30},  # Parentheses
        ]
        
        for case in test_cases:
            try:
                payload = {
                    "expression": case["expression"],
                    "mode": "basic",
                    "session_id": self.session_id
                }
                
                response = requests.post(f"{self.api_url}/calculate", json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    result = float(data.get("result", 0))
                    
                    if abs(result - case["expected"]) < 0.0001:  # Float comparison
                        self.log_test(f"Basic Calc: {case['expression']}", True, f"Result: {result}")
                    else:
                        self.log_test(f"Basic Calc: {case['expression']}", False, 
                                    f"Expected: {case['expected']}, Got: {result}")
                else:
                    self.log_test(f"Basic Calc: {case['expression']}", False, 
                                f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Basic Calc: {case['expression']}", False, f"Exception: {str(e)}")

    def test_scientific_calculations(self):
        """Test scientific calculations"""
        test_cases = [
            {"expression": "sin(0)", "expected": 0},
            {"expression": "cos(0)", "expected": 1},
            {"expression": "sqrt(16)", "expected": 4},
            {"expression": "log(10)", "expected": 1},  # log10
            {"expression": "pi", "expected": 3.14159, "tolerance": 0.001},
            {"expression": "e", "expected": 2.71828, "tolerance": 0.001},
        ]
        
        for case in test_cases:
            try:
                payload = {
                    "expression": case["expression"],
                    "mode": "scientific",
                    "session_id": self.session_id
                }
                
                response = requests.post(f"{self.api_url}/calculate", json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error"):
                        self.log_test(f"Scientific Calc: {case['expression']}", False, 
                                    f"Error: {data['error']}")
                        continue
                        
                    result = float(data.get("result", 0))
                    tolerance = case.get("tolerance", 0.0001)
                    
                    if abs(result - case["expected"]) < tolerance:
                        self.log_test(f"Scientific Calc: {case['expression']}", True, f"Result: {result}")
                    else:
                        self.log_test(f"Scientific Calc: {case['expression']}", False, 
                                    f"Expected: {case['expected']}, Got: {result}")
                else:
                    self.log_test(f"Scientific Calc: {case['expression']}", False, 
                                f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Scientific Calc: {case['expression']}", False, f"Exception: {str(e)}")

    def test_programming_mode(self):
        """Test programming mode with different number systems"""
        test_cases = [
            {"expression": "255", "number_system": "hexadecimal", "expected_format": "FF"},
            {"expression": "16", "number_system": "hexadecimal", "expected_format": "10"},
            {"expression": "8", "number_system": "octal", "expected_format": "10"},
            {"expression": "15", "number_system": "binary", "expected_format": "1111"},
        ]
        
        for case in test_cases:
            try:
                payload = {
                    "expression": case["expression"],
                    "mode": "programming",
                    "number_system": case["number_system"],
                    "session_id": self.session_id
                }
                
                response = requests.post(f"{self.api_url}/calculate", json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error"):
                        self.log_test(f"Programming Mode: {case['expression']} to {case['number_system']}", 
                                    False, f"Error: {data['error']}")
                        continue
                        
                    formatted_result = data.get("formatted_result", "")
                    
                    if formatted_result == case["expected_format"]:
                        self.log_test(f"Programming Mode: {case['expression']} to {case['number_system']}", 
                                    True, f"Result: {formatted_result}")
                    else:
                        self.log_test(f"Programming Mode: {case['expression']} to {case['number_system']}", 
                                    False, f"Expected: {case['expected_format']}, Got: {formatted_result}")
                else:
                    self.log_test(f"Programming Mode: {case['expression']} to {case['number_system']}", 
                                False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Programming Mode: {case['expression']} to {case['number_system']}", 
                            False, f"Exception: {str(e)}")

    def test_number_conversion(self):
        """Test POST /api/convert-number"""
        test_cases = [
            {"value": "255", "from_base": "decimal", "to_base": "hexadecimal", "expected": "FF"},
            {"value": "FF", "from_base": "hexadecimal", "to_base": "decimal", "expected": "255"},
            {"value": "10", "from_base": "octal", "to_base": "decimal", "expected": "8"},
            {"value": "1111", "from_base": "binary", "to_base": "decimal", "expected": "15"},
        ]
        
        for case in test_cases:
            try:
                payload = {
                    "value": case["value"],
                    "from_base": case["from_base"],
                    "to_base": case["to_base"]
                }
                
                response = requests.post(f"{self.api_url}/convert-number", json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    converted = data.get("converted", "")
                    
                    if converted == case["expected"]:
                        self.log_test(f"Number Conversion: {case['value']} {case['from_base']} to {case['to_base']}", 
                                    True, f"Result: {converted}")
                    else:
                        self.log_test(f"Number Conversion: {case['value']} {case['from_base']} to {case['to_base']}", 
                                    False, f"Expected: {case['expected']}, Got: {converted}")
                else:
                    self.log_test(f"Number Conversion: {case['value']} {case['from_base']} to {case['to_base']}", 
                                False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Number Conversion: {case['value']} {case['from_base']} to {case['to_base']}", 
                            False, f"Exception: {str(e)}")

    def test_financial_calculations(self):
        """Test POST /api/financial-calculation"""
        test_cases = [
            {
                "calculation_type": "compound_interest",
                "parameters": {"principal": 1000, "rate": 0.05, "time": 2, "n": 1},
                "expected_min": 1100,  # Should be around 1102.5
                "expected_max": 1110
            },
            {
                "calculation_type": "loan_payment",
                "parameters": {"principal": 10000, "rate": 0.05, "periods": 12},
                "expected_min": 1100,  # Monthly payment should be reasonable
                "expected_max": 1200
            },
            {
                "calculation_type": "present_value",
                "parameters": {"future_value": 1000, "rate": 0.05, "periods": 2},
                "expected_min": 900,  # Should be around 907
                "expected_max": 920
            }
        ]
        
        for case in test_cases:
            try:
                payload = {
                    "calculation_type": case["calculation_type"],
                    "parameters": case["parameters"]
                }
                
                response = requests.post(f"{self.api_url}/financial-calculation", json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("result", 0)
                    
                    if case["expected_min"] <= result <= case["expected_max"]:
                        self.log_test(f"Financial Calc: {case['calculation_type']}", True, f"Result: {result}")
                    else:
                        self.log_test(f"Financial Calc: {case['calculation_type']}", False, 
                                    f"Result {result} not in expected range [{case['expected_min']}, {case['expected_max']}]")
                else:
                    self.log_test(f"Financial Calc: {case['calculation_type']}", False, 
                                f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Financial Calc: {case['calculation_type']}", False, f"Exception: {str(e)}")

    def test_history_operations(self):
        """Test history GET and DELETE operations"""
        # First, ensure we have some calculations in history
        self.test_basic_calculations()
        time.sleep(1)  # Give time for database operations
        
        # Test GET history
        try:
            response = requests.get(f"{self.api_url}/history/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                history = data.get("history", [])
                count = data.get("count", 0)
                
                if count > 0 and len(history) > 0:
                    self.log_test("Get History", True, f"Retrieved {count} history items")
                else:
                    self.log_test("Get History", False, f"No history found, count: {count}")
            else:
                self.log_test("Get History", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get History", False, f"Exception: {str(e)}")
        
        # Test DELETE history
        try:
            response = requests.delete(f"{self.api_url}/history/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get("deleted_count", 0)
                
                if deleted_count > 0:
                    self.log_test("Clear History", True, f"Deleted {deleted_count} history items")
                else:
                    self.log_test("Clear History", False, f"No items deleted, count: {deleted_count}")
            else:
                self.log_test("Clear History", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Clear History", False, f"Exception: {str(e)}")

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        error_cases = [
            {"expression": "1/0", "mode": "basic", "description": "Division by zero"},
            {"expression": "invalid_function()", "mode": "scientific", "description": "Invalid function"},
            {"expression": "", "mode": "basic", "description": "Empty expression"},
        ]
        
        for case in error_cases:
            try:
                payload = {
                    "expression": case["expression"],
                    "mode": case["mode"],
                    "session_id": self.session_id
                }
                
                response = requests.post(f"{self.api_url}/calculate", json=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("error") or data.get("result") == "Error":
                        self.log_test(f"Error Handling: {case['description']}", True, 
                                    f"Properly handled error: {data.get('error', 'Error result')}")
                    else:
                        self.log_test(f"Error Handling: {case['description']}", False, 
                                    f"Should have returned error but got: {data}")
                else:
                    # HTTP error codes are also acceptable for error handling
                    self.log_test(f"Error Handling: {case['description']}", True, 
                                f"HTTP error code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Error Handling: {case['description']}", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all test suites"""
        print("=" * 60)
        print("ADVANCED CALCULATOR API COMPREHENSIVE TESTS")
        print("=" * 60)
        print()
        
        # Run all test suites
        self.test_health_endpoint()
        self.test_basic_calculations()
        self.test_scientific_calculations()
        self.test_programming_mode()
        self.test_number_conversion()
        self.test_financial_calculations()
        self.test_history_operations()
        self.test_error_handling()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
            print()
        
        return passed_tests, failed_tests, self.test_results

if __name__ == "__main__":
    tester = CalculatorAPITester()
    passed, failed, results = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)