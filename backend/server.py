from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import math
import numpy as np
from datetime import datetime
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Advanced Calculator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL')
client = MongoClient(MONGO_URL)
db = client.calculator_db
history_collection = db.calculation_history

# Pydantic models
class CalculationRequest(BaseModel):
    expression: str
    mode: str = "basic"  # basic, scientific, financial, programming
    number_system: str = "decimal"  # decimal, octal, hexadecimal
    session_id: Optional[str] = None

class CalculationResponse(BaseModel):
    result: str
    formatted_result: str
    expression: str
    mode: str
    number_system: str
    timestamp: str
    calculation_id: str
    error: Optional[str] = None

class NumberConversionRequest(BaseModel):
    value: str
    from_base: str  # decimal, octal, hexadecimal, binary
    to_base: str

class FinancialCalculationRequest(BaseModel):
    calculation_type: str  # compound_interest, loan_payment, present_value, etc.
    parameters: Dict[str, float]

# Helper functions for number system conversions
def convert_number_base(value: str, from_base: str, to_base: str) -> str:
    """Convert number between different bases"""
    try:
        # Convert to decimal first
        if from_base == "decimal":
            decimal_value = int(float(value))
        elif from_base == "binary":
            decimal_value = int(value, 2)
        elif from_base == "octal":
            decimal_value = int(value, 8)
        elif from_base == "hexadecimal":
            decimal_value = int(value, 16)
        else:
            raise ValueError(f"Unsupported base: {from_base}")
        
        # Convert from decimal to target base
        if to_base == "decimal":
            return str(decimal_value)
        elif to_base == "binary":
            return bin(decimal_value)[2:]
        elif to_base == "octal":
            return oct(decimal_value)[2:]
        elif to_base == "hexadecimal":
            return hex(decimal_value)[2:].upper()
        else:
            raise ValueError(f"Unsupported base: {to_base}")
            
    except Exception as e:
        raise ValueError(f"Conversion error: {str(e)}")

# Scientific calculator functions
def safe_eval_scientific(expression: str) -> float:
    """Safely evaluate scientific expressions"""
    # Replace common functions with numpy equivalents
    expression = expression.replace("sin", "np.sin")
    expression = expression.replace("cos", "np.cos")
    expression = expression.replace("tan", "np.tan")
    expression = expression.replace("log", "np.log10")
    expression = expression.replace("ln", "np.log")
    expression = expression.replace("sqrt", "np.sqrt")
    expression = expression.replace("exp", "np.exp")
    expression = expression.replace("pi", "np.pi")
    expression = expression.replace("e", "np.e")
    expression = expression.replace("^", "**")
    
    # Safe evaluation with limited scope
    allowed_names = {
        "np": np,
        "math": math,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "log": np.log10,
        "ln": np.log,
        "sqrt": np.sqrt,
        "exp": np.exp,
        "pi": np.pi,
        "e": np.e,
        "abs": abs,
        "pow": pow,
        "round": round
    }
    
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")

# Financial calculations
def calculate_compound_interest(principal: float, rate: float, time: float, n: float = 1) -> float:
    """Calculate compound interest: A = P(1 + r/n)^(nt)"""
    return principal * (1 + rate/n) ** (n * time)

def calculate_loan_payment(principal: float, rate: float, periods: float) -> float:
    """Calculate monthly loan payment using PMT formula"""
    if rate == 0:
        return principal / periods
    return principal * (rate * (1 + rate)**periods) / ((1 + rate)**periods - 1)

def calculate_present_value(future_value: float, rate: float, periods: float) -> float:
    """Calculate present value: PV = FV / (1 + r)^n"""
    return future_value / (1 + rate) ** periods

# Computer logic operations
def bitwise_operation(a: int, b: int, operation: str) -> int:
    """Perform bitwise operations"""
    operations = {
        "AND": lambda x, y: x & y,
        "OR": lambda x, y: x | y,
        "XOR": lambda x, y: x ^ y,
        "NOT": lambda x, y: ~x,
        "LSHIFT": lambda x, y: x << y,
        "RSHIFT": lambda x, y: x >> y
    }
    
    if operation not in operations:
        raise ValueError(f"Unsupported operation: {operation}")
    
    return operations[operation](a, b)

# API Routes

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Advanced Calculator API"}

@app.post("/api/calculate", response_model=CalculationResponse)
async def calculate(request: CalculationRequest):
    """Main calculation endpoint"""
    calculation_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    try:
        result = None
        formatted_result = ""
        
        if request.mode == "basic":
            # Basic arithmetic
            result = eval(request.expression.replace("^", "**"))
            formatted_result = str(result)
            
        elif request.mode == "scientific":
            # Scientific calculations
            result = safe_eval_scientific(request.expression)
            formatted_result = f"{result:.10g}"
            
        elif request.mode == "programming":
            # Handle programming mode with different number systems
            if request.number_system != "decimal":
                # Convert expression to decimal, calculate, then convert back
                # This is a simplified approach - would need more complex parsing for full support
                result = eval(request.expression.replace("^", "**"))
                decimal_result = int(result)
                if request.number_system == "hexadecimal":
                    formatted_result = hex(decimal_result)[2:].upper()
                elif request.number_system == "octal":
                    formatted_result = oct(decimal_result)[2:]
                elif request.number_system == "binary":
                    formatted_result = bin(decimal_result)[2:]
            else:
                result = eval(request.expression.replace("^", "**"))
                formatted_result = str(result)
        
        # Store in database
        calculation_doc = {
            "calculation_id": calculation_id,
            "expression": request.expression,
            "result": str(result),
            "formatted_result": formatted_result,
            "mode": request.mode,
            "number_system": request.number_system,
            "timestamp": timestamp,
            "session_id": request.session_id or "default"
        }
        
        history_collection.insert_one(calculation_doc)
        
        return CalculationResponse(
            result=str(result),
            formatted_result=formatted_result,
            expression=request.expression,
            mode=request.mode,
            number_system=request.number_system,
            timestamp=timestamp,
            calculation_id=calculation_id
        )
        
    except Exception as e:
        return CalculationResponse(
            result="Error",
            formatted_result="Error",
            expression=request.expression,
            mode=request.mode,
            number_system=request.number_system,
            timestamp=timestamp,
            calculation_id=calculation_id,
            error=str(e)
        )

@app.post("/api/convert-number")
async def convert_number(request: NumberConversionRequest):
    """Convert numbers between different bases"""
    try:
        result = convert_number_base(request.value, request.from_base, request.to_base)
        return {"original": request.value, "converted": result, "from_base": request.from_base, "to_base": request.to_base}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/financial-calculation")
async def financial_calculation(request: FinancialCalculationRequest):
    """Perform financial calculations"""
    try:
        if request.calculation_type == "compound_interest":
            result = calculate_compound_interest(
                request.parameters["principal"],
                request.parameters["rate"],
                request.parameters["time"],
                request.parameters.get("n", 1)
            )
        elif request.calculation_type == "loan_payment":
            result = calculate_loan_payment(
                request.parameters["principal"],
                request.parameters["rate"],
                request.parameters["periods"]
            )
        elif request.calculation_type == "present_value":
            result = calculate_present_value(
                request.parameters["future_value"],
                request.parameters["rate"],
                request.parameters["periods"]
            )
        else:
            raise ValueError(f"Unsupported calculation type: {request.calculation_type}")
        
        return {"calculation_type": request.calculation_type, "result": result, "parameters": request.parameters}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/history/{session_id}")
async def get_calculation_history(session_id: str, limit: int = 50):
    """Get calculation history for a session"""
    try:
        history = list(history_collection.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit))
        
        return {"session_id": session_id, "history": history, "count": len(history)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{session_id}")
async def clear_calculation_history(session_id: str):
    """Clear calculation history for a session"""
    try:
        result = history_collection.delete_many({"session_id": session_id})
        return {"session_id": session_id, "deleted_count": result.deleted_count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)