from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import random

app = FastAPI(title="Construction AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ProjectData(BaseModel):
    name: str
    budget: float
    duration: int
    projectType: str
    location: str
    clientHistory: Optional[str] = "unknown"

class PredictionRequest(BaseModel):
    type: str
    data: Optional[dict] = None
    projectId: Optional[str] = None
    months: Optional[int] = 12

class PredictionResponse(BaseModel):
    prediction: dict
    confidence: float

# Simple ML Models (Mock)
def calculate_risk_score(project_data):
    """Calculate risk score based on project parameters"""
    base_score = 50
    
    # Budget factor
    if project_data.get('budget', 0) > 1000000000:
        base_score += 15
    
    # Duration factor
    if project_data.get('duration', 0) > 24:
        base_score += 10
    
    # Client history factor
    client_history = project_data.get('clientHistory', 'unknown')
    if client_history == 'good':
        base_score -= 20
    elif client_history == 'poor':
        base_score += 25
    
    return min(100, max(0, base_score))

def predict_profit(project_data):
    """Predict profit margin for a project"""
    base_profit = 8.0
    
    # Adjust based on project type
    project_type = project_data.get('projectType', 'building')
    type_adjustment = {
        'building': 2.0,
        'factory': 1.5,
        'infrastructure': 1.0,
        'renovation': 3.0
    }.get(project_type, 0)
    
    # Random variation
    variation = random.uniform(-2.0, 3.0)
    
    return max(1.0, min(20.0, base_profit + type_adjustment + variation))

def generate_profit_forecast(months=12):
    """Generate profit forecast over time"""
    forecast = []
    current_profit = 5.0
    
    for i in range(months):
        # Random walk with slight upward trend
        change = random.uniform(-1.5, 2.0)
        current_profit += change
        current_profit = max(0, min(25, current_profit))
        
        forecast.append({
            'month': i + 1,
            'predicted': round(current_profit, 2),
            'optimistic': round(current_profit + random.uniform(1, 3), 2),
            'pessimistic': round(max(0, current_profit - random.uniform(1, 3)), 2)
        })
    
    return forecast

# Routes
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ai-service"}

@app.post("/predict")
async def predict(request: PredictionRequest):
    """Make predictions based on project data"""
    
    if request.type == "pre_project":
        data = request.data or {}
        risk_score = calculate_risk_score(data)
        predicted_profit = predict_profit(data)
        
        # Determine recommendation
        if risk_score < 40 and predicted_profit > 10:
            recommendation = "ACCEPT"
            should_accept = True
        elif risk_score < 60 and predicted_profit > 7:
            recommendation = "ACCEPT_WITH_CAUTION"
            should_accept = True
        elif risk_score < 80:
            recommendation = "NEGOTIATE"
            should_accept = False
        else:
            recommendation = "REJECT"
            should_accept = False
        
        return {
            "prediction": {
                "shouldAccept": should_accept,
                "predictedProfit": round(predicted_profit, 2),
                "riskScore": risk_score,
                "confidence": round(random.uniform(0.75, 0.95), 2),
                "factors": [
                    {"name": "Client History", "score": random.randint(60, 95), "impact": "positive" if random.random() > 0.3 else "negative"},
                    {"name": "Material Cost Trend", "score": random.randint(50, 90), "impact": "negative" if random.random() > 0.5 else "positive"},
                    {"name": "Labor Availability", "score": random.randint(70, 95), "impact": "positive"},
                    {"name": "Market Conditions", "score": random.randint(55, 85), "impact": random.choice(["positive", "negative"])},
                ],
                "recommendation": recommendation,
                "estimatedRoi": round(predicted_profit * 1.2, 2)
            }
        }
    
    elif request.type == "anomaly_detection":
        # Mock anomaly detection
        return {
            "prediction": {
                "anomaliesDetected": random.random() > 0.7,
                "anomalyScore": round(random.uniform(0, 100), 2),
                "alerts": [
                    {"type": "cost", "severity": "medium", "message": "Cost variance detected"} if random.random() > 0.7 else None,
                    {"type": "schedule", "severity": "low", "message": "Slight delay expected"} if random.random() > 0.8 else None,
                ],
                "recommendations": [
                    "Review material procurement strategy",
                    "Optimize resource allocation"
                ]
            }
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unknown prediction type")

@app.post("/forecast")
async def forecast(request: PredictionRequest):
    """Generate forecasts"""
    
    if request.type == "profit":
        forecast_data = generate_profit_forecast(request.months or 12)
        
        avg_profit = sum(f['predicted'] for f in forecast_data) / len(forecast_data)
        trend = "UP" if forecast_data[-1]['predicted'] > forecast_data[0]['predicted'] else "DOWN"
        
        return {
            "forecast": forecast_data,
            "summary": {
                "avgProfit": round(avg_profit, 2),
                "trend": trend,
                "confidence": round(random.uniform(0.82, 0.96), 2),
                "projectedROI": round(avg_profit * 1.15, 2)
            }
        }
    
    elif request.type == "resource":
        return {
            "forecast": [
                {"month": i+1, "laborNeeded": random.randint(50, 100), "equipmentNeeded": random.randint(10, 30)}
                for i in range(request.months or 12)
            ]
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unknown forecast type")

@app.post("/analyze/esg")
async def analyze_esg(request: dict):
    """Analyze ESG metrics"""
    
    return {
        "esgScore": {
            "environmental": round(random.uniform(70, 95), 1),
            "social": round(random.uniform(75, 95), 1),
            "governance": round(random.uniform(80, 95), 1),
            "overall": round(random.uniform(75, 92), 1)
        },
        "carbonFootprint": {
            "current": round(random.uniform(100, 500), 2),
            "projected": round(random.uniform(80, 450), 2),
            "reduction": round(random.uniform(5, 20), 1)
        },
        "recommendations": [
            "Switch to renewable energy sources",
            "Implement waste recycling program",
            "Enhance employee safety training"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
