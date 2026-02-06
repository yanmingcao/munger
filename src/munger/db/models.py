"""SQLAlchemy database models."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class UserProfileDB(Base):
    """User profile database model."""

    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Background (stored as JSON for flexibility)
    background: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Constraints
    constraints: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Preferences
    preferences: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Free-form bio
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    charter: Mapped["CharterDB | None"] = relationship(
        "CharterDB", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    events: Mapped[list["LifeEventDB"]] = relationship(
        "LifeEventDB", back_populates="user", cascade="all, delete-orphan"
    )
    conversations: Mapped[list["ConversationDB"]] = relationship(
        "ConversationDB", back_populates="user", cascade="all, delete-orphan"
    )


class CharterDB(Base):
    """Personal values charter database model."""

    __tablename__ = "charters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id"), nullable=False, unique=True
    )

    # Values and goals (stored as JSON arrays)
    values: Mapped[list[str]] = mapped_column(JSON, default=list)
    non_negotiables: Mapped[list[str]] = mapped_column(JSON, default=list)
    long_term_goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    anti_goals: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Boundaries
    remember_topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    forget_topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    sensitive_topics: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["UserProfileDB"] = relationship("UserProfileDB", back_populates="charter")


class LifeEventDB(Base):
    """Life event database model."""

    __tablename__ = "life_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id"), nullable=False
    )

    # Event details
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Context (stored as JSON)
    people_involved: Mapped[list[str]] = mapped_column(JSON, default=list)
    emotions: Mapped[list[str]] = mapped_column(JSON, default=list)
    significance: Mapped[int] = mapped_column(Integer, default=5)

    # Learning and follow-up
    lessons_learned: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    related_events: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["UserProfileDB"] = relationship("UserProfileDB", back_populates="events")


class ConversationDB(Base):
    """Conversation database model."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id"), nullable=False
    )

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Session context
    session_mood: Mapped[str | None] = mapped_column(String(100), nullable=True)
    session_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["UserProfileDB"] = relationship("UserProfileDB", back_populates="conversations")
    messages: Mapped[list["MessageDB"]] = relationship(
        "MessageDB", back_populates="conversation", cascade="all, delete-orphan"
    )


class MessageDB(Base):
    """Message database model."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False
    )

    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Metadata
    mental_models_used: Mapped[list[str]] = mapped_column(JSON, default=list)
    sources_cited: Mapped[list[str]] = mapped_column(JSON, default=list)
    context_used: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    conversation: Mapped["ConversationDB"] = relationship(
        "ConversationDB", back_populates="messages"
    )
