"""Data models for Sentinel using SQLAlchemy and Pydantic schemas."""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship
from pydantic import BaseModel, Field

Base = declarative_base()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ItemModel(Base):
    """Normalized ingested item from sources (arXiv, HF, GitHub, RSS, HN)."""
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(64), nullable=False)
    external_id = Column(String(256), nullable=False)
    canonical_url = Column(String(1024), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    author = Column(String(256), nullable=True)
    published_at = Column(DateTime, default=utc_now)
    retrieved_at = Column(DateTime, default=utc_now)
    source_type = Column(String(64), nullable=False)
    reliability_tier = Column(Integer, default=5)
    content_hash = Column(String(64), nullable=False, index=True)
    excerpt = Column(Text, nullable=True)
    story_id = Column(String(36), nullable=True, index=True)
    category = Column(String(64), default="general")
    
    # Intelligence & Scoring
    importance_score = Column(Float, default=0.0)
    personal_relevance_score = Column(Float, default=0.0)
    priority = Column(String(32), default="WATCH")  # MUST_KNOW, SHOULD_KNOW, LEARN, WATCH, IGNORE
    status = Column(String(32), default="new")       # new, scored, analyzed, delivered, dropped
    
    # Analytical outputs
    summary = Column(Text, nullable=True)
    why_it_matters = Column(Text, nullable=True)
    what_changed = Column(Text, nullable=True)
    practical_action = Column(Text, nullable=True)
    epistemic_marker = Column(String(32), default="📣") # ✅, 📣, 🧩, 🎯, ❓
    hype_flag = Column(Boolean, default=False)
    contradiction_flag = Column(Boolean, default=False)
    
    claims = relationship("ClaimModel", back_populates="item", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_item_source_external", "source_id", "external_id", unique=True),
    )


class ClaimModel(Base):
    """Extractable factual claim with epistemic confidence and source evidence."""
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String(36), ForeignKey("items.id"), nullable=False)
    claim_type = Column(String(64), nullable=False)  # benchmark, license, capability, hardware, date
    text = Column(Text, nullable=False)
    value_num = Column(Float, nullable=True)
    unit = Column(String(32), nullable=True)
    verification_level = Column(Integer, default=1)  # 0: unverified, 1: self-claim, 2: corroborated, 3: independent
    epistemic_label = Column(String(32), default="SOURCE_CLAIM")
    evidence_url = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    item = relationship("ItemModel", back_populates="claims")


class UserSkillModel(Base):
    """Living skill inventory with 3-dimensional confidence."""
    __tablename__ = "user_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    skill_name = Column(String(128), nullable=False)
    track = Column(String(32), default="AI")          # AI or DATA
    theory_confidence = Column(Float, default=0.5)     # 0.0 to 1.0
    practice_confidence = Column(Float, default=0.5)
    production_confidence = Column(Float, default=0.3)
    last_reviewed = Column(DateTime, default=utc_now)
    decay_rate = Column(Float, default=0.05)


class WorkImpactLogModel(Base):
    """Work Impact Log (/win) capturing measurable accomplishments for appraisals and 1on1s."""
    __tablename__ = "work_impact_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    metric_before = Column(String(128), nullable=True)
    metric_after = Column(String(128), nullable=True)
    impact_summary = Column(Text, nullable=True)
    linked_skills = Column(String(256), nullable=True)
    confidentiality = Column(String(32), default="abstracted")  # abstracted, private-local, public


class UserJournalModel(Base):
    """Tracks what the user works on, what they learned, and their specific interests."""
    __tablename__ = "user_journal"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    entry_type = Column(String(32), nullable=False)  # work, learned, interest
    content = Column(Text, nullable=False)
    tags = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=utc_now)


class ChatMessageModel(Base):
    """Stores multi-turn conversational history between user and bot."""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    role = Column(String(16), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)


class UserMemoryModel(Base):
    """Long-term memory storing explicit and inferred user facts, preferences, and context."""
    __tablename__ = "user_memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False, index=True)
    memory_text = Column(Text, nullable=False)
    category = Column(String(32), default="fact")  # preference, work, learning, fact
    created_at = Column(DateTime, default=utc_now)




class ProviderUsageModel(Base):
    """Tracks token consumption and enforces DB-level $0 cost check constraint."""
    __tablename__ = "provider_usage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String(64), nullable=False)
    model = Column(String(128), nullable=False)
    day = Column(String(10), nullable=False)  # YYYY-MM-DD
    requests = Column(Integer, default=0)
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    est_cost_usd = Column(Float, default=0.0)

    __table_args__ = (
        CheckConstraint("est_cost_usd <= 0.000001", name="check_zero_dollar_budget"),
        Index("idx_provider_day", "provider", "model", "day", unique=True),
    )


# --- Pydantic Schemas for API & Business Logic ---

class ItemSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    external_id: str
    canonical_url: str
    title: str
    author: Optional[str] = None
    published_at: datetime = Field(default_factory=utc_now)
    source_type: str
    reliability_tier: int = 5
    content_hash: str
    excerpt: Optional[str] = None
    category: str = "general"
    importance_score: float = 0.0
    personal_relevance_score: float = 0.0
    priority: str = "WATCH"
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    what_changed: Optional[str] = None
    practical_action: Optional[str] = None
    epistemic_marker: str = "📣"
    hype_flag: bool = False
    contradiction_flag: bool = False
