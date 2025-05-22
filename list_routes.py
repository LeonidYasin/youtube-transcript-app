from app.main import app

def list_routes():
    print("\nRegistered routes in the FastAPI application:")
    print("-" * 80)
    for route in app.routes:
        print(f"{route.path} - {route.name} - {route.methods}")
    print("-" * 80)

if __name__ == "__main__":
    list_routes()
