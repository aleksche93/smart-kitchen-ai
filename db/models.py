import uuid
from sqlalchemy import Column, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.types as types

Base = declarative_base()

class GUID(types.TypeDecorator):
    """Platform-independent GUID type."""
    impl = types.CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return "%.32x" % uuid.UUID(value).int
        return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value

class UserModel(Base):
    __tablename__ = 'users'
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, default="ChefUser")
    preferred_language = Column(String, default='uk')

class ChefStateModel(Base):
    """Stores the strictly relational core state of the Chef FSM."""
    __tablename__ = 'chef_state'
    user_id = Column(GUID(), primary_key=True)
    current_state = Column(String, nullable=False, default='IDLE')
    emotion_value = Column(Float, nullable=False, default=0.0)
    personality_profile = Column(String, default='neutral')

class ChefMemoryModel(Base):
    """Stores flexible JSON properties for preferences, long term metrics, etc."""
    __tablename__ = 'chef_memory'
    user_id = Column(GUID(), primary_key=True)
    preferences = Column(JSON, default=dict)       # Likes/dislikes
    traits = Column(JSON, default=dict)            # Playful, chaotic, etc.
    cooking_sins = Column(JSON, default=dict)      # Tuna welldone, overcooked shrimp
    long_term_counters = Column(JSON, default=dict) # Respect, toxicity trackers

class ChefSessionModel(Base):
    """Contextual short-term memory loaded on request start."""
    __tablename__ = 'chef_session'
    user_id = Column(GUID(), primary_key=True)
    recent_triggers = Column(JSON, default=list) # Short-term memory history
    ui_events = Column(JSON, default=list)       # UI session history

class InventoryItemModel(Base):
    """Stores all user inventory items with smart categorization and expiration logic."""
    __tablename__ = 'inventory_items'
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), default=uuid.uuid4) # Foreign key loosely implied
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    storage_location = Column(String, nullable=False, default='Fridge')
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="pcs")
    price = Column(Float, nullable=True)
    added_date = Column(String, nullable=False) # Store ISO formatted date string
    expiry_date = Column(String, nullable=True) # Null for non-perishables

from datetime import datetime

class ReceiptHistoryModel(Base):
    __tablename__ = 'receipt_history'
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    image_hash = Column(String(64), unique=True, index=True, nullable=False)
    scan_date = Column(String, default=lambda: datetime.utcnow().isoformat())
