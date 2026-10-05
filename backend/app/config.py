import os
from app.db.database import engine, Base

# Create SQLite database
Base.metadata.create_all(bind=engine)

# Later implementations can add more server configs here.
# For now, it initializes the DB and environment variables.
