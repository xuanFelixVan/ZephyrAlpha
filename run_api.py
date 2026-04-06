#!/usr/bin/env python
"""
ZephyrAlpha API启动脚本

使用方法:
    python run_api.py

或使用uvicorn:
    uvicorn src.api.main:app --reload --port 8000
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
    print("ZephyrAlpha量化交易系统 API")
    print("=" * 50)
    print()
    print("📚 API文档地址:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc:      http://localhost:8000/redoc")
    print("   - OpenAPI:    http://localhost:8000/openapi.json")
    print()
    print("🔧 可用端点:")
    print("   - GET  /              - API根路径")
    print("   - GET  /health       - 健康检查")
    print("   - GET  /api/strategies     - 策略列表")
    print("   - POST /api/backtest/run   - 执行回测")
    print("   - GET  /api/monitoring     - 监控数据")
    print()
    print("=" * 50)
    print()
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
