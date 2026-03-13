"""
Trend Predictor Service Entry Point
"""
import os
import sys
sys.path.insert(0, '/app/modules')

from module_11_trend_predictor import TrendPredictor

if __name__ == "__main__":
    import asyncio
    import time
    
    predictor = TrendPredictor()
    
    async def main():
        print("🚀 Trend Predictor started")
        print("🔍 Monitoring trends every hour...")
        
        while True:
            try:
                # Run analysis every hour
                report = predictor.analyze_trends(hours=24)
                
                # Check for critical trends
                critical = [t for t in report.trends 
                           if t.alert_level.value == "critical"]
                
                if critical:
                    print(f"🚨 {len(critical)} critical trends detected!")
                    # Could send alert to admin here
                
                # Save report
                predictor.generate_report_file(report, 
                    f"/tmp/trend_report_{int(time.time())}.json")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Wait 1 hour
            await asyncio.sleep(3600)
    
    asyncio.run(main())
