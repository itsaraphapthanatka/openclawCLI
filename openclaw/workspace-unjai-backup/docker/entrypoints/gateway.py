"""
LINE Gateway Service Entry Point - Integrated with Swarm
"""
import os
import sys

# เพิ่ม path เพื่อให้หาโมดูลในโฟลเดอร์ modules เจอ
sys.path.insert(0, '/app/modules')

# Import integrated gateway
from integrated_gateway import get_integrated_gateway

if __name__ == "__main__":
    import uvicorn
    
    # 1. สร้าง Integrated Gateway (พร้อม Pinecone + LINE)
    gateway = get_integrated_gateway()
    
    # 2. สร้าง FastAPI app
    app = gateway.get_app()
    
    # ดึงค่า Config จาก Environment Variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 Starting LINE Gateway with Pinecone Integration on {host}:{port}")
    print(f"   BASE_URL: {os.getenv('BASE_URL', 'NOT SET')}")
    print(f"   PINECONE_API_KEY: {'SET' if os.getenv('PINECONE_API_KEY') else 'NOT SET'}")
    print(f"   PINECONE_HOST: {os.getenv('PINECONE_INDEX_HOST', 'NOT SET')}")
    
    uvicorn.run(app, host=host, port=port)
