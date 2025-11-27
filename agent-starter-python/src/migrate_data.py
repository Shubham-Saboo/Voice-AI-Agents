#!/usr/bin/env python3
"""
Migration script to load provider data from JSON into SQLite
No PostgreSQL credentials needed - uses SQLite by default!
"""
import json
import os
import sys
import logging
from pathlib import Path
from database import db, Provider, provider_insurance, provider_language

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migrate")


def load_providers_from_json(json_path: str) -> list:
    """Load providers from JSON file"""
    with open(json_path, 'r') as f:
        providers = json.load(f)
    logger.info(f"Loaded {len(providers)} providers from {json_path}")
    return providers


def migrate_to_database(providers: list):
    """Migrate providers to SQLite/PostgreSQL with junction tables"""
    db.init_db()
    session = db.get_session()
    
    try:
        # Clear existing data (cascade will handle junction tables)
        session.query(Provider).delete()
        session.commit()
        logger.info("Cleared existing provider data")
        
        # Insert providers and populate junction tables
        for provider in providers:
            address = provider.get("address", {})
            
            db_provider = Provider(
                id=provider["id"],
                first_name=provider["first_name"],
                last_name=provider["last_name"],
                full_name=provider["full_name"],
                specialty=provider["specialty"],
                phone=provider["phone"],
                email=provider["email"],
                street=address.get("street", ""),
                city=address.get("city", ""),
                state=address.get("state", ""),
                zip_code=address.get("zip", ""),
                years_experience=provider.get("years_experience", 0),
                accepting_new_patients=provider.get("accepting_new_patients", True),
                rating=provider.get("rating", 0.0),
                license_number=provider.get("license_number", ""),
                board_certified=provider.get("board_certified", False),
                # JSON columns kept for backward compatibility (optional)
                insurance_accepted=provider.get("insurance_accepted", []),
                languages=provider.get("languages", []),
            )
            
            session.add(db_provider)
            session.flush()  # Flush to get the provider ID
            
            # Populate insurance junction table
            for insurance in provider.get("insurance_accepted", []):
                session.execute(
                    provider_insurance.insert().values(
                        provider_id=provider["id"],
                        insurance=insurance
                    )
                )
            
            # Populate language junction table
            for language in provider.get("languages", []):
                session.execute(
                    provider_language.insert().values(
                        provider_id=provider["id"],
                        language=language
                    )
                )
        
        session.commit()
        logger.info(f"Successfully migrated {len(providers)} providers to database")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error migrating to database: {e}")
        raise
    finally:
        session.close()




def main():
    """Main migration function"""
    # Get JSON file path
    json_path = os.getenv(
        "PROVIDER_JSON_PATH",
        str(Path(__file__).parent.parent.parent / "vox-takehome-test" / "data" / "providerlist.json")
    )
    
    if not os.path.exists(json_path):
        logger.error(f"Provider JSON file not found: {json_path}")
        sys.exit(1)
    
    # Load providers
    providers = load_providers_from_json(json_path)
    
    migrate_to_database(providers)
    logger.info("Migration completed successfully")


if __name__ == "__main__":
    main()


