"""
Analytics Dashboard Service Entry Point
"""
import os
import sys
sys.path.insert(0, '/app/modules')

from module_9_analytics import AnalyticsDashboard, create_dashboard_api

if __name__ == "__main__":
    import uvicorn
    
    analytics = AnalyticsDashboard()
    app = create_dashboard_api(analytics)
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8002"))
    
    print(f"🚀 Starting Analytics Dashboard on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
