from app.main import app

print("Registered routes:")
for route in app.routes:
    if hasattr(route, 'path'):
        methods = getattr(route, 'methods', [])
        path = getattr(route, 'path', '')
        print(f"{path} - {methods}")
