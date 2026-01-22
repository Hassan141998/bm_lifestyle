from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Connecting to database...")
    # diverse SQL to cover both SQLite and Postgres syntax if needed, but here target is Postgres
    try:
        # Postgres syntax
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE product ALTER COLUMN image_file TYPE TEXT;"))
            conn.commit()
        print("Successfully changed image_file to TEXT.")
    except Exception as e:
        print(f"Error: {e}")
