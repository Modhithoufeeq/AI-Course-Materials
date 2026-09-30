import sys
import uvicorn
from backend.app.core.config import settings
from backend.app.database.seed import seed_database

if __name__ == "__main__":
    if "--seed" in sys.argv or "-s" in sys.argv:
        print("Running database seed...")
        seed_database()
        print("Seed completed.")
    
    print(f"Starting {settings.PROJECT_NAME} backend on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
