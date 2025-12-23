#!/usr/bin/env python3
"""Script to create database migration for new features."""
import subprocess
import sys


def create_migration():
    """Create Alembic migration for multi-tenant, logger, and compliance tables."""
    print("Creating database migration...")
    print("=" * 60)
    
    migration_message = (
        "Add multi-tenant, logging, and compliance tables\n\n"
        "This migration adds:\n"
        "- Multi-tenant support (schema-per-tenant)\n"
        "- Compliance tables (consents, audit logs, retention)\n"
        "- Data subject rights tracking\n"
        "- Encryption key management"
    )
    
    try:
        # Create migration
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", migration_message],
            check=True,
            capture_output=True,
            text=True,
        )
        
        print("✅ Migration created successfully!")
        print(result.stdout)
        
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Review the generated migration file in alembic/versions/")
        print("2. Apply the migration: alembic upgrade head")
        print("3. Create your first tenant: POST /api/v1/tenants")
        print("=" * 60)
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print("❌ Error creating migration:")
        print(e.stderr)
        return 1
    except FileNotFoundError:
        print("❌ Error: Alembic not found. Please install dependencies first:")
        print("   uv sync")
        print("   or")
        print("   pip install -e .")
        return 1


if __name__ == "__main__":
    sys.exit(create_migration())

