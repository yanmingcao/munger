"""Main advisor service - orchestrates RAG and response generation."""

from collections.abc import Iterator
from typing import Any
from uuid import UUID

from munger.advisor.llm import generate_response
from munger.core.config import settings
from munger.core.models import (
    Charter,
    Conversation,
    LifeEvent,
    Message,
    MessageRole,
    UserProfile,
)
from munger.db.database import get_session
from munger.db.repository import (
    CharterRepository,
    ConversationRepository,
    EventRepository,
    UserRepository,
)
from munger.db.vector_store import WisdomVectorStore
from munger.persona.mental_models import get_relevant_models
from munger.persona.prompts import assemble_full_prompt, build_reflection_prompt


class MungerAdvisor:
    """The Charlie Munger personal advisor."""

    def __init__(self):
        """Initialize the advisor."""
        self._vector_store: WisdomVectorStore | None = None

    @property
    def vector_store(self) -> WisdomVectorStore:
        """Lazy-load vector store."""
        if self._vector_store is None:
            self._vector_store = WisdomVectorStore()
        return self._vector_store

    def ask(
        self,
        question: str,
        user_id: UUID | str | None = None,
        session_context: str | None = None,
        stream: bool = False,
    ) -> str | Iterator[str]:
        """
        Ask Charlie Munger for advice.

        Args:
            question: The question to ask
            user_id: Optional user ID for personalization
            session_context: Optional context about current session/mood
            stream: Whether to stream the response

        Returns:
            The advice response (or iterator if streaming)
        """
        # Load user context
        profile, charter, recent_events = self._load_user_context(user_id)

        # Retrieve relevant wisdom
        relevant_wisdom = self._retrieve_wisdom(question)

        # Get relevant mental models
        relevant_models = get_relevant_models(question)

        # Assemble prompt
        messages = assemble_full_prompt(
            question=question,
            profile=profile,
            charter=charter,
            recent_events=recent_events,
            relevant_wisdom=relevant_wisdom,
            relevant_models=relevant_models,
            session_context=session_context,
        )

        # Generate response
        response = generate_response(messages, stream=stream)

        # Store conversation if we have a user
        if user_id and not stream:
            self._store_conversation(
                user_id=user_id,
                question=question,
                response=response if isinstance(response, str) else "",
                models_used=[m.name for m in relevant_models],
                wisdom_sources=[w.get("metadata", {}).get("title", "") for w in relevant_wisdom],
            )

        return response

    def chat(
        self,
        message: str,
        conversation_id: UUID | str | None = None,
        user_id: UUID | str | None = None,
        stream: bool = False,
    ) -> tuple[str | Iterator[str], UUID]:
        """
        Continue a chat conversation.

        Args:
            message: The user message
            conversation_id: Optional existing conversation ID
            user_id: Optional user ID
            stream: Whether to stream the response

        Returns:
            Tuple of (response, conversation_id)
        """
        with get_session() as session:
            conv_repo = ConversationRepository(session)

            # Get or create conversation
            if conversation_id:
                conversation = conv_repo.get(conversation_id)
                if not conversation:
                    raise ValueError(f"Conversation not found: {conversation_id}")
            else:
                # Get default user if not specified
                if not user_id:
                    user_repo = UserRepository(session)
                    profile = user_repo.get_default()
                    if not profile:
                        raise ValueError("No user profile found. Run 'munger init' first.")
                    user_id = profile.id

                # Create new conversation
                conversation = Conversation(user_id=user_id)
                conv_repo.create(conversation)

            # Add user message
            conv_repo.add_message(
                conversation.id,
                MessageRole.USER,
                message,
            )

            # Build context from conversation history
            history_context = self._format_conversation_history(conversation)

            # Generate response
            response = self.ask(
                question=message,
                user_id=user_id,
                session_context=history_context,
                stream=stream,
            )

            # Store assistant response
            if not stream:
                conv_repo.add_message(
                    conversation.id,
                    MessageRole.ASSISTANT,
                    response if isinstance(response, str) else "",
                )

            return response, conversation.id

    def reflect(
        self,
        user_id: UUID | str | None = None,
        stream: bool = False,
    ) -> str | Iterator[str]:
        """
        Conduct a reflection session.

        Args:
            user_id: Optional user ID
            stream: Whether to stream the response

        Returns:
            The reflection response
        """
        with get_session() as session:
            # Get user context
            user_repo = UserRepository(session)
            charter_repo = CharterRepository(session)
            event_repo = EventRepository(session)

            if user_id:
                profile = user_repo.get(user_id)
            else:
                profile = user_repo.get_default()

            if not profile:
                raise ValueError("No user profile found. Run 'munger init' first.")

            charter = charter_repo.get_by_user(profile.id)
            recent_events = event_repo.list_by_user(profile.id, limit=10)

            # Build reflection prompt
            messages = build_reflection_prompt(
                profile=profile,
                charter=charter,
                recent_events=recent_events,
            )

            # Generate response
            return generate_response(messages, stream=stream)

    def _load_user_context(
        self,
        user_id: UUID | str | None,
    ) -> tuple[UserProfile | None, Charter | None, list[LifeEvent] | None]:
        """Load user context from database."""
        if not user_id:
            # Try to get default user
            with get_session() as session:
                user_repo = UserRepository(session)
                profile = user_repo.get_default()
                if profile:
                    user_id = profile.id
                else:
                    return None, None, None

        with get_session() as session:
            user_repo = UserRepository(session)
            charter_repo = CharterRepository(session)
            event_repo = EventRepository(session)

            profile = user_repo.get(user_id)
            charter = charter_repo.get_by_user(user_id) if profile else None
            recent_events = event_repo.get_recent(user_id) if profile else None

            return profile, charter, recent_events

    def _retrieve_wisdom(self, question: str) -> list[dict[str, Any]]:
        """Retrieve relevant wisdom from vector store."""
        try:
            return self.vector_store.search(
                query=question,
                n_results=settings.retrieval_top_k,
            )
        except Exception:
            # Vector store might be empty or not initialized
            return []

    def _store_conversation(
        self,
        user_id: UUID | str,
        question: str,
        response: str,
        models_used: list[str],
        wisdom_sources: list[str],
    ) -> None:
        """Store a Q&A exchange."""
        with get_session() as session:
            conv_repo = ConversationRepository(session)

            conversation = Conversation(user_id=UUID(str(user_id)))
            conv_repo.create(conversation)

            # Add user message
            conv_repo.add_message(
                conversation.id,
                MessageRole.USER,
                question,
            )

            # Add assistant response
            conv_repo.add_message(
                conversation.id,
                MessageRole.ASSISTANT,
                response,
                mental_models_used=models_used,
                sources_cited=wisdom_sources,
            )

            # End conversation (single Q&A)
            conv_repo.end_conversation(conversation.id)

    def _format_conversation_history(self, conversation: Conversation) -> str:
        """Format conversation history for context."""
        if not conversation.messages:
            return ""

        lines = ["Previous conversation:"]
        for msg in conversation.messages[-10:]:  # Last 10 messages
            role = "You" if msg.role == MessageRole.USER else "Munger"
            lines.append(f"{role}: {msg.content[:500]}")

        return "\n".join(lines)


# Singleton instance
advisor = MungerAdvisor()
