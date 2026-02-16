"""
Database initialization script.
Creates all tables and optionally seeds demo data.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Base, engine, SessionLocal
from app.models import Activity, Alert, FileScan, ModelMetrics
from app.services.activity_service import generate_fake_activity, ActivityService
import random
from datetime import datetime, timedelta


def create_tables():
    """Create all database tables."""
    print("\n📦 Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def seed_demo_data():
    """Seed database with demo data."""
    print("\n🌱 Seeding demo data...")

    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Activity).count() > 0:
            print("⚠ Database already contains data. Skipping seed.")
            return True

        # Create demo activities
        print("  → Creating demo activities...")
        service = ActivityService(db)

        for i in range(50):
            activity_data = generate_fake_activity()

            # Randomly adjust timestamp to spread across last 24 hours
            hours_ago = random.uniform(0, 24)

            activity = service.create_activity(activity_data)

            # Update timestamp to spread data
            activity.timestamp = datetime.utcnow() - timedelta(hours=hours_ago)

        db.commit()
        print(f"  ✓ Created 50 demo activities")

        # Create demo file scans
        print("  → Creating demo file scans...")
        filenames = [
            "document.pdf",
            "image.jpg",
            "report.xlsx",
            "suspicious.exe",
            "malware.dll",
            "script.bat",
            "data.csv",
            "backup.zip"
        ]

        for i, filename in enumerate(filenames):
            scan_result = random.choices(
                ['safe', 'suspicious', 'malicious'],
                weights=[0.7, 0.2, 0.1]
            )[0]

            file_scan = FileScan(
                filename=filename,
                file_hash=f"{'0' * (64 - len(str(i)))}{i}",  # Fake hash
                file_size=random.randint(1024, 10485760),
                file_type=os.path.splitext(filename)[1],
                scan_result=scan_result,
                confidence_score=random.uniform(0.7, 0.99),
                is_quarantined=scan_result in ['suspicious', 'malicious'],
                scanned_by="demo@example.com",
                scan_timestamp=datetime.utcnow() - timedelta(hours=random.uniform(0, 48))
            )
            db.add(file_scan)

        db.commit()
        print(f"  ✓ Created {len(filenames)} demo file scans")

        # Get counts
        activity_count = db.query(Activity).count()
        suspicious_count = db.query(Activity).filter(Activity.is_suspicious == True).count()
        alert_count = db.query(Alert).count()
        scan_count = db.query(FileScan).count()

        print("\n" + "="*60)
        print("SEED DATA SUMMARY")
        print("="*60)
        print(f"Activities: {activity_count} (Suspicious: {suspicious_count})")
        print(f"Alerts: {alert_count}")
        print(f"File Scans: {scan_count}")
        print("="*60)

        return True

    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main initialization function."""
    print("\n" + "="*60)
    print("🗄️  DATABASE INITIALIZATION")
    print("="*60)

    # Create tables
    if not create_tables():
        print("\n✗ Database initialization failed")
        sys.exit(1)

    # Seed demo data
    if not seed_demo_data():
        print("\n⚠ Demo data seeding failed (but tables are created)")

    print("\n" + "="*60)
    print("✓ Database initialization complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
