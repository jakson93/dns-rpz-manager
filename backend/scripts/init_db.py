#!/usr/bin/env python3
"""
DNS RPZ Manager - Database Initialization Script

This script initializes the PostgreSQL database with the required tables
and creates a default admin user for the application.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.user import User
from app.models.domain import Domain
from app.models.audit_log import AuditLog


async def create_database():
    """Create the database if it doesn't exist."""
    # Connect without database name to create it
    db_url = settings.DATABASE_URL.replace(
        settings.POSTGRES_DB, "postgres"
    )
    
    engine = create_async_engine(db_url, echo=True)
    
    async with engine.connect() as conn:
        # Check if database exists
        result = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'"
            )
        )
        exists = result.scalar()
        
        if not exists:
            # Create database
            await conn.execute(text(f"CREATE DATABASE {settings.POSTGRES_DB}"))
            print(f"Database '{settings.POSTGRES_DB}' created successfully.")
        else:
            print(f"Database '{settings.POSTGRES_DB}' already exists.")
    
    await engine.dispose()


async def create_tables():
    """Create all tables defined in the models."""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("All tables created successfully.")
    
    await engine.dispose()


async def create_admin_user():
    """Create the default admin user."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check if admin user exists
            result = await session.execute(
                text("SELECT id FROM users WHERE username = 'admin'")
            )
            exists = result.scalar()
            
            if not exists:
                # Create admin user
                hashed_password = get_password_hash("admin123")
                await session.execute(
                    text(
                        """
                        INSERT INTO users (username, email, hashed_password, full_name, 
                                          role, is_active, created_at, updated_at)
                        VALUES (:username, :email, :password, :full_name, 
                               :role, :is_active, NOW(), NOW())
                        """
                    ),
                    {
                        "username": "admin",
                        "email": "admin@dnsrpz.local",
                        "password": hashed_password,
                        "full_name": "System Administrator",
                        "role": "admin",
                        "is_active": True,
                    },
                )
                await session.commit()
                print("Admin user created successfully (username: admin, password: admin123)")
            else:
                print("Admin user already exists.")
        
        except Exception as e:
            await session.rollback()
            print(f"Error creating admin user: {e}")
            raise
        finally:
            await session.close()
    
    await engine.dispose()


async def create_sample_data():
    """Create sample RPZ entries for testing."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Check if sample domains exist
            result = await session.execute(
                text("SELECT COUNT(*) FROM domains")
            )
            count = result.scalar()
            
            if count == 0:
                # Create sample blocked domains
                sample_domains = [
                    {
                        "domain": "malware-example.com",
                        "action": "nxdomain",
                        "reason": "Sample malware domain for testing",
                        "source": "test-data",
                        "is_active": True,
                    },
                    {
                        "domain": "phishing-example.net",
                        "action": "nxdomain",
                        "reason": "Sample phishing domain for testing",
                        "source": "test-data",
                        "is_active": True,
                    },
                    {
                        "domain": "spam-example.org",
                        "action": "passthru",
                        "reason": "Sample spam domain for testing",
                        "source": "test-data",
                        "is_active": False,
                    },
                ]
                
                for domain_data in sample_domains:
                    await session.execute(
                        text(
                            """
                            INSERT INTO domains (domain, action, reason, source, 
                                                is_active, created_at, updated_at)
                            VALUES (:domain, :action, :reason, :source, 
                                   :is_active, NOW(), NOW())
                            """
                        ),
                        domain_data,
                    )
                
                await session.commit()
                print("Sample domain data created successfully.")
            else:
                print(f"Domains table already has {count} entries. Skipping sample data.")
        
        except Exception as e:
            await session.rollback()
            print(f"Error creating sample data: {e}")
            raise
        finally:
            await session.close()
    
    await engine.dispose()


async def main():
    """Main initialization function."""
    print("=" * 60)
    print("DNS RPZ Manager - Database Initialization")
    print("=" * 60)
    
    try:
        print("\n[1/4] Creating database...")
        await create_database()
        
        print("\n[2/4] Creating tables...")
        await create_tables()
        
        print("\n[3/4] Creating admin user...")
        await create_admin_user()
        
        print("\n[4/4] Creating sample data...")
        await create_sample_data()
        
        print("\n" + "=" * 60)
        print("Database initialization completed successfully!")
        print("=" * 60)
        print("\nYou can now start the application with:")
        print("  docker-compose up -d")
        print("\nDefault admin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("=" * 60)
    
    except Exception as e:
        print(f"\nError during initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
