"""Repository layer for database operations."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from munger.core.models import (
    Background,
    Charter,
    Constraints,
    Conversation,
    EventCategory,
    LifeEvent,
    Message,
    MessageRole,
    Preferences,
    UserProfile,
)
from munger.db.models import (
    CharterDB,
    ConversationDB,
    LifeEventDB,
    MessageDB,
    UserProfileDB,
)


class UserRepository:
    """Repository for user profile operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, profile: UserProfile) -> UserProfile:
        """Create a new user profile."""
        db_profile = UserProfileDB(
            id=str(profile.id),
            name=profile.name,
            background=profile.background.model_dump(),
            constraints=profile.constraints.model_dump(),
            preferences=profile.preferences.model_dump(),
            bio=profile.bio,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
        self.session.add(db_profile)
        self.session.flush()
        return profile

    def get(self, user_id: UUID | str) -> UserProfile | None:
        """Get user profile by ID."""
        db_profile = self.session.get(UserProfileDB, str(user_id))
        if not db_profile:
            return None
        return self._to_domain(db_profile)

    def get_default(self) -> UserProfile | None:
        """Get the default (first) user profile."""
        db_profile = self.session.query(UserProfileDB).first()
        if not db_profile:
            return None
        return self._to_domain(db_profile)

    def update(self, profile: UserProfile) -> UserProfile:
        """Update an existing user profile."""
        db_profile = self.session.get(UserProfileDB, str(profile.id))
        if not db_profile:
            raise ValueError(f"User profile not found: {profile.id}")

        db_profile.name = profile.name
        db_profile.background = profile.background.model_dump()
        db_profile.constraints = profile.constraints.model_dump()
        db_profile.preferences = profile.preferences.model_dump()
        db_profile.bio = profile.bio
        db_profile.updated_at = datetime.utcnow()

        self.session.flush()
        return profile

    def delete(self, user_id: UUID | str) -> bool:
        """Delete a user profile."""
        db_profile = self.session.get(UserProfileDB, str(user_id))
        if not db_profile:
            return False
        self.session.delete(db_profile)
        return True

    def _to_domain(self, db_profile: UserProfileDB) -> UserProfile:
        """Convert database model to domain model."""
        return UserProfile(
            id=UUID(db_profile.id),
            name=db_profile.name,
            background=Background(**db_profile.background),
            constraints=Constraints(**db_profile.constraints),
            preferences=Preferences(**db_profile.preferences),
            bio=db_profile.bio,
            created_at=db_profile.created_at,
            updated_at=db_profile.updated_at,
        )


class CharterRepository:
    """Repository for charter operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, charter: Charter) -> Charter:
        """Create a new charter."""
        db_charter = CharterDB(
            id=str(charter.id),
            user_id=str(charter.user_id),
            values=charter.values,
            non_negotiables=charter.non_negotiables,
            long_term_goals=charter.long_term_goals,
            anti_goals=charter.anti_goals,
            remember_topics=charter.remember_topics,
            forget_topics=charter.forget_topics,
            sensitive_topics=charter.sensitive_topics,
            created_at=charter.created_at,
            updated_at=charter.updated_at,
        )
        self.session.add(db_charter)
        self.session.flush()
        return charter

    def get_by_user(self, user_id: UUID | str) -> Charter | None:
        """Get charter by user ID."""
        db_charter = (
            self.session.query(CharterDB)
            .filter(CharterDB.user_id == str(user_id))
            .first()
        )
        if not db_charter:
            return None
        return self._to_domain(db_charter)

    def update(self, charter: Charter) -> Charter:
        """Update an existing charter."""
        db_charter = self.session.get(CharterDB, str(charter.id))
        if not db_charter:
            raise ValueError(f"Charter not found: {charter.id}")

        db_charter.values = charter.values
        db_charter.non_negotiables = charter.non_negotiables
        db_charter.long_term_goals = charter.long_term_goals
        db_charter.anti_goals = charter.anti_goals
        db_charter.remember_topics = charter.remember_topics
        db_charter.forget_topics = charter.forget_topics
        db_charter.sensitive_topics = charter.sensitive_topics
        db_charter.updated_at = datetime.utcnow()

        self.session.flush()
        return charter

    def _to_domain(self, db_charter: CharterDB) -> Charter:
        """Convert database model to domain model."""
        return Charter(
            id=UUID(db_charter.id),
            user_id=UUID(db_charter.user_id),
            values=db_charter.values,
            non_negotiables=db_charter.non_negotiables,
            long_term_goals=db_charter.long_term_goals,
            anti_goals=db_charter.anti_goals,
            remember_topics=db_charter.remember_topics,
            forget_topics=db_charter.forget_topics,
            sensitive_topics=db_charter.sensitive_topics,
            created_at=db_charter.created_at,
            updated_at=db_charter.updated_at,
        )


class EventRepository:
    """Repository for life event operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, event: LifeEvent) -> LifeEvent:
        """Create a new life event."""
        db_event = LifeEventDB(
            id=str(event.id),
            user_id=str(event.user_id),
            date=event.date,
            title=event.title,
            description=event.description,
            category=event.category.value,
            people_involved=event.people_involved,
            emotions=event.emotions,
            significance=event.significance,
            lessons_learned=event.lessons_learned,
            follow_up_date=event.follow_up_date,
            related_events=[str(e) for e in event.related_events],
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
        self.session.add(db_event)
        self.session.flush()
        return event

    def get(self, event_id: UUID | str) -> LifeEvent | None:
        """Get event by ID."""
        db_event = self.session.get(LifeEventDB, str(event_id))
        if not db_event:
            return None
        return self._to_domain(db_event)

    def list_by_user(
        self,
        user_id: UUID | str,
        category: EventCategory | None = None,
        limit: int = 50,
        min_significance: int = 1,
    ) -> list[LifeEvent]:
        """List events for a user."""
        query = (
            self.session.query(LifeEventDB)
            .filter(LifeEventDB.user_id == str(user_id))
            .filter(LifeEventDB.significance >= min_significance)
        )

        if category:
            query = query.filter(LifeEventDB.category == category.value)

        query = query.order_by(LifeEventDB.date.desc()).limit(limit)

        return [self._to_domain(db_event) for db_event in query.all()]

    def get_recent(
        self, user_id: UUID | str, limit: int = 10
    ) -> list[LifeEvent]:
        """Get recent significant events."""
        return self.list_by_user(user_id, limit=limit, min_significance=5)

    def update(self, event: LifeEvent) -> LifeEvent:
        """Update an existing event."""
        db_event = self.session.get(LifeEventDB, str(event.id))
        if not db_event:
            raise ValueError(f"Event not found: {event.id}")

        db_event.date = event.date
        db_event.title = event.title
        db_event.description = event.description
        db_event.category = event.category.value
        db_event.people_involved = event.people_involved
        db_event.emotions = event.emotions
        db_event.significance = event.significance
        db_event.lessons_learned = event.lessons_learned
        db_event.follow_up_date = event.follow_up_date
        db_event.related_events = [str(e) for e in event.related_events]
        db_event.updated_at = datetime.utcnow()

        self.session.flush()
        return event

    def delete(self, event_id: UUID | str) -> bool:
        """Delete an event."""
        db_event = self.session.get(LifeEventDB, str(event_id))
        if not db_event:
            return False
        self.session.delete(db_event)
        return True

    def _to_domain(self, db_event: LifeEventDB) -> LifeEvent:
        """Convert database model to domain model."""
        return LifeEvent(
            id=UUID(db_event.id),
            user_id=UUID(db_event.user_id),
            date=db_event.date,
            title=db_event.title,
            description=db_event.description,
            category=EventCategory(db_event.category),
            people_involved=db_event.people_involved,
            emotions=db_event.emotions,
            significance=db_event.significance,
            lessons_learned=db_event.lessons_learned,
            follow_up_date=db_event.follow_up_date,
            related_events=[UUID(e) for e in db_event.related_events],
            created_at=db_event.created_at,
            updated_at=db_event.updated_at,
        )


class ConversationRepository:
    """Repository for conversation operations."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, conversation: Conversation) -> Conversation:
        """Create a new conversation."""
        db_conversation = ConversationDB(
            id=str(conversation.id),
            user_id=str(conversation.user_id),
            title=conversation.title,
            session_mood=conversation.session_mood,
            session_context=conversation.session_context,
            started_at=conversation.started_at,
            ended_at=conversation.ended_at,
        )
        self.session.add(db_conversation)
        self.session.flush()

        # Add messages
        for msg in conversation.messages:
            self._add_message(db_conversation.id, msg)

        return conversation

    def get(self, conversation_id: UUID | str) -> Conversation | None:
        """Get conversation by ID."""
        db_conv = self.session.get(ConversationDB, str(conversation_id))
        if not db_conv:
            return None
        return self._to_domain(db_conv)

    def get_latest(self, user_id: UUID | str) -> Conversation | None:
        """Get the most recent conversation."""
        db_conv = (
            self.session.query(ConversationDB)
            .filter(ConversationDB.user_id == str(user_id))
            .order_by(ConversationDB.started_at.desc())
            .first()
        )
        if not db_conv:
            return None
        return self._to_domain(db_conv)

    def list_by_user(
        self, user_id: UUID | str, limit: int = 20
    ) -> list[Conversation]:
        """List conversations for a user."""
        db_convs = (
            self.session.query(ConversationDB)
            .filter(ConversationDB.user_id == str(user_id))
            .order_by(ConversationDB.started_at.desc())
            .limit(limit)
            .all()
        )
        return [self._to_domain(db_conv) for db_conv in db_convs]

    def add_message(
        self,
        conversation_id: UUID | str,
        role: MessageRole,
        content: str,
        **kwargs: Any,
    ) -> Message:
        """Add a message to an existing conversation."""
        message = Message(role=role, content=content, **kwargs)
        self._add_message(str(conversation_id), message)
        return message

    def _add_message(self, conversation_id: str, message: Message) -> None:
        """Internal method to add a message."""
        db_message = MessageDB(
            id=str(message.id),
            conversation_id=conversation_id,
            role=message.role.value,
            content=message.content,
            timestamp=message.timestamp,
            mental_models_used=message.mental_models_used,
            sources_cited=message.sources_cited,
            context_used=message.context_used,
        )
        self.session.add(db_message)
        self.session.flush()

    def end_conversation(self, conversation_id: UUID | str) -> None:
        """Mark a conversation as ended."""
        db_conv = self.session.get(ConversationDB, str(conversation_id))
        if db_conv:
            db_conv.ended_at = datetime.utcnow()
            self.session.flush()

    def _to_domain(self, db_conv: ConversationDB) -> Conversation:
        """Convert database model to domain model."""
        messages = [
            Message(
                id=UUID(msg.id),
                role=MessageRole(msg.role),
                content=msg.content,
                timestamp=msg.timestamp,
                mental_models_used=msg.mental_models_used,
                sources_cited=msg.sources_cited,
                context_used=msg.context_used,
            )
            for msg in sorted(db_conv.messages, key=lambda m: m.timestamp)
        ]

        return Conversation(
            id=UUID(db_conv.id),
            user_id=UUID(db_conv.user_id),
            title=db_conv.title,
            messages=messages,
            session_mood=db_conv.session_mood,
            session_context=db_conv.session_context,
            started_at=db_conv.started_at,
            ended_at=db_conv.ended_at,
        )
