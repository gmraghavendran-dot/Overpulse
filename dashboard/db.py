from sqlalchemy import create_engine

# -------------------------------------------------------
# PostgreSQL Database Configuration
# -------------------------------------------------------

DB_USER = "postgres"
DB_PASSWORD = "raga2005"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "data_obs"

# -------------------------------------------------------
# Database URL
# -------------------------------------------------------

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# -------------------------------------------------------
# SQLAlchemy Engine
# -------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

# -------------------------------------------------------
# Test Connection (Optional)
# -------------------------------------------------------

if __name__ == "__main__":
    try:
        connection = engine.connect()
        print("✅ Connected to PostgreSQL Successfully!")
        connection.close()
    except Exception as e:
        print("❌ Database Connection Failed!")
        print(e)