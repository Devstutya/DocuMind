# backend/app/rag/memory.py
"""In-process conversation memory with a sliding window and TTL-based expiry.

Stores the last N turns per conversation_id in memory (no database persistence).
Expired conversations are lazily cleaned up on the next access.
"""

from collections import defaultdict
from datetime import datetime, timedelta


class ConversationMemory:
    """Sliding-window in-memory conversation store.

    Keeps the last ``max_turns`` question/answer pairs per conversation and
    automatically discards conversations that have been idle for longer than
    ``ttl_minutes``.

    Args:
        max_turns: Maximum number of turns to retain per conversation.
            Older turns are dropped when this limit is exceeded.
        ttl_minutes: Number of minutes of inactivity before a conversation
            is considered expired and removed on the next cleanup pass.
    """

    def __init__(self, max_turns: int = 5, ttl_minutes: int = 30):
        self.conversations: dict[str, list[dict]] = defaultdict(list)
        self.max_turns = max_turns
        self.ttl = timedelta(minutes=ttl_minutes)
        self.last_access: dict[str, datetime] = {}

    def add_turn(self, conversation_id: str, question: str, answer: str) -> None:
        """Append a Q&A turn to the conversation and enforce the window limit.

        Args:
            conversation_id: Unique identifier for the conversation session.
            question: The user's question text.
            answer: The assistant's answer text.
        """
        self.conversations[conversation_id].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow(),
        })
        # Enforce sliding window — keep only the most recent max_turns turns.
        if len(self.conversations[conversation_id]) > self.max_turns:
            self.conversations[conversation_id] = (
                self.conversations[conversation_id][-self.max_turns:]
            )
        self.last_access[conversation_id] = datetime.utcnow()

    def get_history(self, conversation_id: str) -> list[dict]:
        """Return the conversation history for a given session.

        Triggers a cleanup pass for expired sessions before returning.

        Args:
            conversation_id: The session to retrieve history for.

        Returns:
            List of turn dicts (each with ``question``, ``answer``,
            ``timestamp`` keys), oldest first.  Returns an empty list if
            the conversation does not exist or has expired.
        """
        self._cleanup_expired()
        return self.conversations.get(conversation_id, [])

    def format_history(self, conversation_id: str) -> str:
        """Return conversation history formatted for prompt injection.

        Produces a plain-text transcript suitable for prepending to the
        current question so the model has context for follow-up answers.

        Args:
            conversation_id: The session to format.

        Returns:
            Multi-line string of alternating ``User:`` and ``Assistant:``
            lines, or an empty string if there is no prior history.

        Example::

            memory.add_turn("abc", "What is RAG?", "It is a technique...")
            print(memory.format_history("abc"))
            # "User: What is RAG?\\nAssistant: It is a technique..."
        """
        history = self.get_history(conversation_id)
        if not history:
            return ""

        formatted = []
        for turn in history:
            formatted.append(f"User: {turn['question']}")
            formatted.append(f"Assistant: {turn['answer']}")
        return "\n".join(formatted)

    def _cleanup_expired(self) -> None:
        """Remove conversations that have exceeded the TTL.

        Called lazily before each ``get_history`` to avoid unbounded memory
        growth in long-running processes.
        """
        now = datetime.utcnow()
        expired = [
            cid
            for cid, last in self.last_access.items()
            if now - last > self.ttl
        ]
        for cid in expired:
            del self.conversations[cid]
            del self.last_access[cid]


# Module-level singleton shared across all requests in the same process.
memory = ConversationMemory()
