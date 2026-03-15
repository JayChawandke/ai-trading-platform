
import sys
import os
sys.path.append(os.getcwd())

from app.main import app

with open("routes.txt", "w") as f:
    for route in app.routes:
        methods = getattr(route, "methods", "WS")
        f.write(f"{methods} {route.path}\n")
print("Wrote routes to routes.txt")
