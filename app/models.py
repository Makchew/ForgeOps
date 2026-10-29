from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Project(Base):
	__tablename__ = "projects"

	id: Mapped[int] = mapped_column(
		Integer,
		primary_key=True,
		index=True,
	)
	name: Mapped[str] = mapped_column(
		String(100),
		nullable=False,
	)
	description: Mapped[str] = mapped_column(
		Text,
		default="",
		nullable=False,
	)

