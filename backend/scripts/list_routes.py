
import sys
import os
sys.path.append(os.getcwd())

try:
    from app.main import app
    print("--- FastAPI ROUTES ---")
    for route in app.routes:
        methods = getattr(route, "methods", "WS")
        print(f"{methods} {route.path}")
    print("----------------------")
except Exception as e:
    print(f"Error: {e}")
