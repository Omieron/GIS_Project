from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Import routers
from routers.location_router import router as location_router
from routers.buildings_router import router as buildings_router

# Configure database connection
DATABASE_URL = "postgresql://postgres:123@localhost:8086/edremit_maks"

# Create SQLAlchemy engine with a timeout to prevent hanging
try:
    engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 3})
    db_available = True
    print("Database engine created successfully. Testing connection...")
    try:
        # Quick connection test
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database connection verified!")
    except Exception as e:
        print(f"⚠️ Database connectivity test failed: {str(e)}")
        db_available = False
except Exception as e:
    print(f"⚠️ Error initializing database engine: {str(e)}")
    engine = None
    db_available = False
    
# Create session factory if engine is available
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

# Dependency for database sessions
def get_db():
    if not db_available:
        raise HTTPException(
            status_code=503, 
            detail="Database connection is not available"
        )
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Smart Location AI")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(location_router)
# Include buildings router
app.include_router(buildings_router)

@app.get("/")
def read_root():
    # Redirect to docs by default
    return RedirectResponse(url="/docs")

@app.get("/health")
def health_check():
    return {
        "status": "backend running",
        "components": {
            "location_service": "active",
            "building_service": "configured",
            "database": "configured"  # Will be updated to "connected" once database is tested
        }
    }

@app.get("/test-db-connection")
def test_db_connection():
    """
    Test the connection to the edremit_maks database.
    This endpoint reports the current database connection status.
    """
    if db_available:
        try:
            # Attempt a quick connection test
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 AS connection_test")).fetchone()
                if result and result[0] == 1:
                    return {
                        "status": "success", 
                        "message": "Database connection successful",
                        "database": DATABASE_URL.split('@')[1]
                    }
                else:
                    return {
                        "status": "error", 
                        "message": "Connection established but query failed"
                    }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Database connection error: {str(e)}",
                "connection_string": DATABASE_URL.split('@')[1]
            }
    else:
        return {
            "status": "error", 
            "message": "Database connection is not available",
            "connection_string": DATABASE_URL.split('@')[1]
        }

@app.get("/list-tables")
def list_database_tables():
    if not db_available:
        return {
            "status": "error", 
            "message": "Database connection is not available"
        }
    """
    List all tables in the edremit_maks database to explore its structure.
    """
    try:
        # Query to get all table names in PostgreSQL
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        # Execute the query and fetch all results
        result = db.execute(query).fetchall()
        
        # Convert the result to a list of table names
        tables = [row[0] for row in result]
        
        return {"status": "success", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tables: {str(e)}")
