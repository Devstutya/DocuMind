# backend/app/db_models.py
"""SQLAlchemy ORM models for the DocuMind application.

All primary-key columns use ``String`` (UUID stored as a plain string) because
SQLite has no native UUID type.  This also keeps the schema portable to
PostgreSQL without changes — just swap the DATABASE_URL.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserModel(Base):
    """Persistent user account."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    documents: Mapped[list["DocumentModel"]] = relationship(
        "DocumentModel", back_populates="owner", cascade="all, delete-orphan"
    )


class DocumentModel(Base):
    """Metadata for an uploaded PDF document."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="documents")
