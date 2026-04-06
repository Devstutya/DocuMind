# backend/app/rag/chain.py
"""LangChain QA chain for RAG answer generation.

Wraps GPT-4o-mini with a system prompt that constrains the model to answer
only from the provided context and cite sources using [Page X] notation.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

_llm = None


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return _llm


SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.

Instructions:
- Answer based ONLY on the provided context
- If the context doesn't contain the answer, say "I couldn't find information about that in the documents"
- Cite your sources using [Page X] format
- Be concise but thorough

Context:
{context}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a single context string for the prompt.

    Each chunk is prefixed with its page number (if available) so the model
    can generate accurate [Page X] citations.

    Args:
        chunks: List of chunk dicts as returned by :func:`query_similar`.
            Each dict may contain ``page`` (int or None) and ``text`` (str).

    Returns:
        A newline-separated string of formatted chunk blocks, separated by
        ``---`` dividers.

    Example::

        context = format_context([{"page": 3, "text": "RAG is useful..."}])
        # "[Page 3]\\nRAG is useful..."
    """
    context_parts = []
    for chunk in chunks:
        source = f"[Page {chunk['page']}]" if chunk.get("page") else ""
        context_parts.append(f"{source}\n{chunk['text']}")
    return "\n\n---\n\n".join(context_parts)


async def generate_answer(question: str, chunks: list[dict]) -> str:
    """Generate an answer to a question from retrieved document chunks.

    Formats the chunks into a context string, injects both into the prompt,
    and streams the response through GPT-4o-mini. Returns the full answer
    as a string.

    Args:
        question: The user's question (may include prepended conversation
            history for follow-up awareness).
        chunks: Retrieved chunks from Pinecone, each with ``text``,
            ``page``, and ``doc_id`` keys.

    Returns:
        The model's answer as a plain string.

    Example::

        answer = await generate_answer("What is RAG?", chunks)
        # "RAG stands for Retrieval-Augmented Generation [Page 1]."
    """
    context = format_context(chunks)
    chain = prompt | _get_llm() | StrOutputParser()
    return await chain.ainvoke({"context": context, "question": question})
