
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class LexicalPosting(Base):
    __tablename__ = "lexical_postings"

    __table_args__ = (
        UniqueConstraint(
            "term_id",
            "chunk_id",
            name="uq_lexical_posting_term_chunk",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    term_id: Mapped[int] = mapped_column(
        ForeignKey(
            "lexical_terms.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    chunk_id: Mapped[int] = mapped_column(
        ForeignKey(
            "chunks.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    term_frequency: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )