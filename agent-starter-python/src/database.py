import os
import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON, Index, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from dotenv import load_dotenv

load_dotenv(".env.local")

logger = logging.getLogger("database")

Base = declarative_base()


provider_insurance = Table(
    'provider_insurance',
    Base.metadata,
    Column('provider_id', Integer, ForeignKey('providers.id', ondelete='CASCADE'), primary_key=True),
    Column('insurance', String(100), primary_key=True),
    Index('idx_provider_insurance_insurance', 'insurance'),
    Index('idx_provider_insurance_provider', 'provider_id'),
)

provider_language = Table(
    'provider_language',
    Base.metadata,
    Column('provider_id', Integer, ForeignKey('providers.id', ondelete='CASCADE'), primary_key=True),
    Column('language', String(100), primary_key=True),
    Index('idx_provider_language_language', 'language'),
    Index('idx_provider_language_provider', 'provider_id'),
)


class Provider(Base):
    __tablename__ = "providers"
    __table_args__ = (
        Index('idx_providers_specialty', 'specialty'),
    )

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False)
    specialty = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(200), nullable=False)
    street = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)
    zip_code = Column(String(10), nullable=False)
    years_experience = Column(Integer, nullable=False)
    accepting_new_patients = Column(Boolean, default=True)
    rating = Column(Float, nullable=False, index=True)
    license_number = Column(String(50), nullable=False)
    board_certified = Column(Boolean, default=False)
    insurance_accepted = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)


class ProviderInsurance(Base):
    __table__ = provider_insurance


class ProviderLanguage(Base):
    __table__ = provider_language


class Database:
    def __init__(self):
        db_url = os.getenv("POSTGRES_URL")
        
        if not db_url:
            db_path = os.getenv("SQLITE_DB_PATH", "./providers.db")
            db_url = f"sqlite:///{db_path}"
        
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def init_db(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def close(self):
        self.engine.dispose()


db = Database()



