from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    All SQLAlchemy ORM models inherit from this.
    Alembic uses this to auto-detect schema changes.
    """
    pass