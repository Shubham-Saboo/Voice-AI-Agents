import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import or_, and_, distinct
from database import db, Provider, provider_insurance, provider_language, ProviderInsurance, ProviderLanguage

logger = logging.getLogger("db_service")


class DatabaseService:
    """Simple SQL-based database service - no vector search"""
    
    def get_available_specialties(self) -> List[str]:
        """Get all distinct specialties from database"""
        session = db.get_session()
        try:
            specialties = session.query(Provider.specialty).distinct().all()
            return [s[0] for s in specialties]
        finally:
            session.close()
    
    def get_available_languages(self) -> List[str]:
        """Get all distinct languages from database using junction table"""
        session = db.get_session()
        try:
            languages = session.query(distinct(ProviderLanguage.language)).all()
            return sorted([lang[0] for lang in languages])
        finally:
            session.close()
    
    def get_available_insurance(self) -> List[str]:
        """Get all distinct insurance types from database using junction table"""
        session = db.get_session()
        try:
            insurance = session.query(distinct(ProviderInsurance.insurance)).all()
            return sorted([ins[0] for ins in insurance])
        finally:
            session.close()
    
    def query_providers(
        self,
        state: Optional[str] = None,
        city: Optional[str] = None,
        specialty: Optional[str] = None,
        language: Optional[str] = None,
        insurance: Optional[str] = None,
        provider_name: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Query providers using SQL with indexed junction tables - fast and scalable"""
        session = db.get_session()
        
        try:
            query = session.query(Provider).distinct()
            conditions = []
            
            # Provider name search
            if provider_name:
                conditions.append(
                    or_(
                        Provider.full_name.ilike(f"%{provider_name}%"),
                        Provider.first_name.ilike(f"%{provider_name}%"),
                        Provider.last_name.ilike(f"%{provider_name}%")
                    )
                )
            
            # Location filters
            if state:
                # State should already be normalized to 2-letter code by LLM
                conditions.append(Provider.state == state.upper())
            
            if city:
                conditions.append(Provider.city.ilike(f"%{city}%"))
            
            # Specialty filter
            if specialty:
                conditions.append(Provider.specialty.ilike(f"%{specialty}%"))
            
            # Language filter (using indexed junction table - FAST!)
            if language:
                query = query.join(provider_language).filter(
                    provider_language.c.language == language
                )
            
            # Insurance filter (using indexed junction table - FAST!)
            if insurance:
                query = query.join(provider_insurance).filter(
                    provider_insurance.c.insurance == insurance
                )
            
            # Apply filters
            if conditions:
                query = query.filter(and_(*conditions))
            
            # Order by rating
            query = query.order_by(Provider.rating.desc())
            
            # Limit results
            providers = query.limit(limit).all()
            
            # Convert to dict (populate JSON arrays from junction tables)
            results = [self._provider_to_dict(p, session) for p in providers]
            logger.info(f"✅ Query returned {len(results)} providers")
            
            return results
            
        finally:
            session.close()
    
    def get_provider_by_id(self, provider_id: int) -> Optional[Dict[str, Any]]:
        """Get provider by ID"""
        session = db.get_session()
        try:
            provider = session.query(Provider).filter(Provider.id == provider_id).first()
            if provider:
                return self._provider_to_dict(provider, session)
            return None
        finally:
            session.close()
    
    def _provider_to_dict(self, provider: Provider, session) -> Dict[str, Any]:
        """Convert Provider model to dictionary, populating arrays from junction tables"""
        # Get insurance from junction table
        insurance_list = session.query(provider_insurance.c.insurance).filter(
            provider_insurance.c.provider_id == provider.id
        ).all()
        insurance_accepted = [ins[0] for ins in insurance_list]
        
        # Get languages from junction table
        language_list = session.query(provider_language.c.language).filter(
            provider_language.c.provider_id == provider.id
        ).all()
        languages = [lang[0] for lang in language_list]
        
        return {
            "id": provider.id,
            "full_name": provider.full_name,
            "first_name": provider.first_name,
            "last_name": provider.last_name,
            "specialty": provider.specialty,
            "phone": provider.phone,
            "email": provider.email,
            "address": {
                "street": provider.street,
                "city": provider.city,
                "state": provider.state,
                "zip": provider.zip_code,
            },
            "years_experience": provider.years_experience,
            "accepting_new_patients": provider.accepting_new_patients,
            "insurance_accepted": insurance_accepted,
            "rating": provider.rating,
            "license_number": provider.license_number,
            "board_certified": provider.board_certified,
            "languages": languages,
        }


# Global instance
db_service = DatabaseService()


