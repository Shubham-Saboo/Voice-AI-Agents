import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import or_, and_, distinct
from database import db, Provider, provider_insurance, provider_language, ProviderInsurance, ProviderLanguage

logger = logging.getLogger("db_service")
# Prevent propagation to root logger to avoid LiveKit's duplicate logging
logger.propagate = False
# Add our own handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


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
        zipcode: Optional[str] = None,
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
            
            if zipcode:
                # Support both 5-digit and ZIP+4 formats
                zipcode_clean = zipcode.replace("-", "").strip()
                conditions.append(Provider.zip_code.ilike(f"%{zipcode_clean}%"))
            
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
            
            # Order by accepting_new_patients first (True first), then by rating
            query = query.order_by(
                Provider.accepting_new_patients.desc(),  # True comes before False
                Provider.rating.desc()
            )
            
            # Limit results
            providers = query.limit(limit).all()
            
            if not providers:
                return []
            
            # Bulk fetch insurance and languages for all providers (avoids N+1 queries)
            provider_ids = [p.id for p in providers]
            
            # Bulk fetch all insurance for these providers (single query instead of N queries)
            insurance_rows = session.query(
                provider_insurance.c.provider_id,
                provider_insurance.c.insurance
            ).filter(
                provider_insurance.c.provider_id.in_(provider_ids)
            ).all()
            insurance_map = {}
            for provider_id, insurance in insurance_rows:
                if provider_id not in insurance_map:
                    insurance_map[provider_id] = []
                insurance_map[provider_id].append(insurance)
            
            # Bulk fetch all languages for these providers (single query instead of N queries)
            language_rows = session.query(
                provider_language.c.provider_id,
                provider_language.c.language
            ).filter(
                provider_language.c.provider_id.in_(provider_ids)
            ).all()
            language_map = {}
            for provider_id, language in language_rows:
                if provider_id not in language_map:
                    language_map[provider_id] = []
                language_map[provider_id].append(language)
            
            # Convert to dict using pre-fetched data (no additional queries)
            results = [
                self._provider_to_dict_fast(p, insurance_map.get(p.id, []), language_map.get(p.id, []))
                for p in providers
            ]
            logger.info(f"✅ Query returned {len(results)} providers")
            
            return results
            
        finally:
            session.close()
    
    def _provider_to_dict_fast(self, provider: Provider, insurance_accepted: List[str], languages: List[str]) -> Dict[str, Any]:
        """Convert Provider model to dictionary using pre-fetched insurance and languages (no DB queries)"""
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


