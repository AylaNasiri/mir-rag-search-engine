
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class LexicalTerm(Base):
    __tablename__ = "lexical_terms"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    term: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )