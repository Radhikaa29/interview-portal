from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:root%401234@localhost:5432/test"  # Update this
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("✅ Database connected successfully!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
