"""Core domain models using Pydantic."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================


class CareerStage(str, Enum):
    """Career stage classification."""

    EARLY = "early"  # 0-5 years
    MID = "mid"  # 5-15 years
    SENIOR = "senior"  # 15-25 years
    EXECUTIVE = "executive"  # 25+ years or C-level
    RETIRED = "retired"


class RiskTolerance(str, Enum):
    """Risk tolerance level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TimeHorizon(str, Enum):
    """Planning time horizon."""

    SHORT = "short"  # < 1 year
    MEDIUM = "medium"  # 1-5 years
    LONG = "long"  # 5-10 years
    VERY_LONG = "very_long"  # 10+ years


class AdviceTone(str, Enum):
    """Preferred advice delivery tone."""

    BLUNT = "blunt"  # Direct, no sugar-coating
    BALANCED = "balanced"  # Direct but considerate
    GENTLE = "gentle"  # More supportive framing


class EventCategory(str, Enum):
    """Life event categories."""

    CAREER = "career"
    FAMILY = "family"
    HEALTH = "health"
    FINANCIAL = "financial"
    RELATIONSHIP = "relationship"
    EDUCATION = "education"
    PERSONAL_GROWTH = "personal_growth"
    OTHER = "other"


# ============================================================================
# User Profile Models
# ============================================================================


class Background(BaseModel):
    """User background information."""

    age: int | None = Field(default=None, ge=0, le=120)
    gender: str | None = None
    nationality: str | None = None
    current_location: str | None = None
    career_stage: CareerStage | None = None
    industry: str | None = None
    occupation: str | None = None
    education_level: str | None = None
    cultural_notes: str | None = Field(
        default=None, description="Cultural context that might influence advice"
    )


class Constraints(BaseModel):
    """User constraints and circumstances."""

    time_horizon: TimeHorizon = TimeHorizon.MEDIUM
    risk_tolerance: RiskTolerance = RiskTolerance.MEDIUM
    has_dependents: bool | None = None
    financial_obligations: str | None = None
    health_considerations: str | None = None
    time_availability: str | None = Field(
        default=None, description="How much time user has for implementing advice"
    )


class Preferences(BaseModel):
    """Advice delivery preferences."""

    tone: AdviceTone = AdviceTone.BALANCED
    depth_level: str = Field(
        default="detailed", description="How detailed responses should be"
    )
    preferred_examples: list[str] = Field(
        default_factory=lambda: ["business", "investing"],
        description="Domains for examples and analogies",
    )
    language: str = Field(default="english", description="Preferred language")


class UserProfile(BaseModel):
    """Complete user profile for personalized advice."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    background: Background = Field(default_factory=Background)
    constraints: Constraints = Field(default_factory=Constraints)
    preferences: Preferences = Field(default_factory=Preferences)
    bio: str | None = Field(
        default=None, description="Free-form biographical information"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def summary(self) -> str:
        """Generate a concise summary for prompt injection."""
        parts = [f"Name: {self.name}"]

        if self.background.age:
            parts.append(f"Age: {self.background.age}")
        if self.background.career_stage:
            parts.append(f"Career stage: {self.background.career_stage.value}")
        if self.background.industry:
            parts.append(f"Industry: {self.background.industry}")
        if self.background.occupation:
            parts.append(f"Occupation: {self.background.occupation}")
        if self.constraints.time_horizon:
            parts.append(f"Time horizon: {self.constraints.time_horizon.value}")
        if self.constraints.risk_tolerance:
            parts.append(f"Risk tolerance: {self.constraints.risk_tolerance.value}")
        if self.constraints.has_dependents is not None:
            parts.append(
                f"Has dependents: {'Yes' if self.constraints.has_dependents else 'No'}"
            )
        if self.background.cultural_notes:
            parts.append(f"Cultural context: {self.background.cultural_notes}")
        if self.bio:
            parts.append(f"Bio: {self.bio}")

        return "; ".join(parts)


# ============================================================================
# Personal Charter
# ============================================================================


class Charter(BaseModel):
    """Personal values charter - what matters most to the user."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID

    # Core values
    values: list[str] = Field(
        default_factory=list,
        description="Core values in priority order (e.g., 'Family first', 'Integrity')",
    )

    # Non-negotiables
    non_negotiables: list[str] = Field(
        default_factory=list,
        description="Things the user will never compromise on",
    )

    # Long-term aims
    long_term_goals: list[str] = Field(
        default_factory=list,
        description="Major life goals and aspirations",
    )

    # Anti-goals (what to avoid)
    anti_goals: list[str] = Field(
        default_factory=list,
        description="Outcomes to actively avoid",
    )

    # Boundaries
    remember_topics: list[str] = Field(
        default_factory=list,
        description="Topics the advisor should always remember and reference",
    )
    forget_topics: list[str] = Field(
        default_factory=list,
        description="Topics to not dwell on or bring up",
    )
    sensitive_topics: list[str] = Field(
        default_factory=list,
        description="Topics requiring extra care",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def summary(self) -> str:
        """Generate a concise summary for prompt injection."""
        parts = []

        if self.values:
            parts.append(f"Core values: {', '.join(self.values[:5])}")
        if self.non_negotiables:
            parts.append(f"Non-negotiables: {', '.join(self.non_negotiables[:3])}")
        if self.long_term_goals:
            parts.append(f"Long-term goals: {', '.join(self.long_term_goals[:3])}")
        if self.anti_goals:
            parts.append(f"Wants to avoid: {', '.join(self.anti_goals[:3])}")

        return "; ".join(parts) if parts else "Charter not yet defined"


# ============================================================================
# Life Events
# ============================================================================


class LifeEvent(BaseModel):
    """A significant life event in the user's journey."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID

    # Event details
    date: datetime
    title: str = Field(description="Brief title of the event")
    description: str = Field(description="Detailed description of what happened")
    category: EventCategory

    # Context
    people_involved: list[str] = Field(
        default_factory=list, description="Key people involved"
    )
    emotions: list[str] = Field(
        default_factory=list, description="Emotions felt during/after"
    )
    significance: int = Field(
        default=5, ge=1, le=10, description="How significant (1-10)"
    )

    # Learning and follow-up
    lessons_learned: str | None = Field(
        default=None, description="What was learned from this event"
    )
    follow_up_date: datetime | None = Field(
        default=None, description="When to check back on this"
    )
    related_events: list[UUID] = Field(
        default_factory=list, description="IDs of related events"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def summary(self) -> str:
        """Generate a concise summary for context."""
        date_str = self.date.strftime("%Y-%m-%d")
        emotions_str = f" (felt: {', '.join(self.emotions)})" if self.emotions else ""
        return f"[{date_str}] {self.title} ({self.category.value}){emotions_str}: {self.description[:200]}"


# ============================================================================
# Conversation History
# ============================================================================


class MessageRole(str, Enum):
    """Message role in conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """A single message in a conversation."""

    id: UUID = Field(default_factory=uuid4)
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Optional metadata
    mental_models_used: list[str] = Field(
        default_factory=list, description="Mental models applied in this response"
    )
    sources_cited: list[str] = Field(
        default_factory=list, description="Munger quotes/sources referenced"
    )
    context_used: dict[str, Any] = Field(
        default_factory=dict, description="User context that influenced the response"
    )


class Conversation(BaseModel):
    """A conversation session with the advisor."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: str | None = Field(default=None, description="Auto-generated or user-set title")
    messages: list[Message] = Field(default_factory=list)

    # Session context
    session_mood: str | None = Field(
        default=None, description="User's emotional state this session"
    )
    session_context: str | None = Field(
        default=None, description="Any specific context for this session"
    )

    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None

    def add_message(self, role: MessageRole, content: str, **kwargs: Any) -> Message:
        """Add a message to the conversation."""
        message = Message(role=role, content=content, **kwargs)
        self.messages.append(message)
        return message


# ============================================================================
# Munger Wisdom
# ============================================================================


class WisdomCategory(str, Enum):
    """Categories of Munger wisdom."""

    MENTAL_MODEL = "mental_model"
    QUOTE = "quote"
    PRINCIPLE = "principle"
    STORY = "story"
    SPEECH_EXCERPT = "speech_excerpt"
    BOOK_EXCERPT = "book_excerpt"


class MungerWisdom(BaseModel):
    """A piece of Charlie Munger's wisdom."""

    id: UUID = Field(default_factory=uuid4)
    category: WisdomCategory
    title: str
    content: str
    source: str = Field(description="Where this came from (book, speech, interview)")
    year: int | None = Field(default=None, description="Year of the source if known")
    tags: list[str] = Field(default_factory=list, description="Topical tags")
    related_models: list[str] = Field(
        default_factory=list, description="Related mental models"
    )

    # For embedding
    embedding: list[float] | None = Field(default=None, exclude=True)
