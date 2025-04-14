"""
Simplified database connection test
"""
import psycopg2

# Connection parameters
DB_HOST = "localhost"
DB_PORT = "8089"
DB_NAME = "edremit_maks"
DB_USER = "postgres"
DB_PASSWORD = "123"

def test_basic_connection():
    """Test basic database connection using psycopg2"""
    print(f"Attempting to connect to PostgreSQL database...")
    print(f"Host: {DB_HOST}")
    print(f"Port: {DB_PORT}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")
    print(f"Password: {'*' * len(DB_PASSWORD)}")
    
    try:
        # Establish connection
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        
        # Get the result
        db_version = cursor.fetchone()
        print(f"\nConnection successful!")
        print(f"PostgreSQL version: {db_version[0]}")
        
        # Close the connection
        cursor.close()
        connection.close()
        print("Connection closed")
        
    except psycopg2.OperationalError as e:
        print(f"\nConnection failed: {str(e)}")
        print("\nPossible issues:")
        print("1. PostgreSQL server is not running on port 8089")
        print("2. The database 'edremit_maks' does not exist")
        print("3. The username or password is incorrect")
        print("4. Firewall is blocking the connection")
        print("\nTry checking if the PostgreSQL server is running and if the database exists.")
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    test_basic_connection()
