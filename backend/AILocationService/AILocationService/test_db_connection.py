"""
Test script to verify PostgreSQL connection to edremit_maks database
"""
import sys
from sqlalchemy import create_engine, text

# Database connection string
DATABASE_URL = "postgresql://postgres:123@localhost:8089/edremit_maks"

def test_connection():
    """Test database connection and print results"""
    print("Testing connection to PostgreSQL database...")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 AS connection_test"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✅ Connection successful!")
                return True
            else:
                print("❌ Query executed but returned unexpected result")
                return False
                
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def list_tables():
    """List all tables in the database"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"\nFound {len(tables)} tables in database:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("\nNo tables found in database")
                
    except Exception as e:
        print(f"❌ Failed to list tables: {str(e)}")

if __name__ == "__main__":
    if test_connection():
        # If connection is successful, try to list tables
        list_tables()
    else:
        sys.exit(1)  # Exit with error
