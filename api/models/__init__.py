# Templated file. Donot modify unless required.
from api.logging_config import setup_logging
import sys
import uuid
import warnings
from sqlalchemy.exc import SAWarning
from sqlalchemy import Boolean, Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, declared_attr, exc, sessionmaker
from sqlalchemy.future import select

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from api import (
    DB_HOST,
    DB_LOGLEVEL,
    DB_MAX_OVERFLOW,
    DB_NAME,
    DB_POOL_SIZE,
    DB_PORT,
    DB_PWORD,
    DB_UNAME,
)
from sqlalchemy.orm import class_mapper

logger = setup_logging(__name__)
logger.info("Initializing DB interactions with %s:%s", DB_HOST, DB_PORT)


# if DB_LOGLEVEL:
#     logging.getLogger("sqlalchemy.engine").setLevel(DB_LOGLEVEL)


DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    username=DB_UNAME,
    password=DB_PWORD,
)

try:
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        echo=False,
    )

    SessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

except Exception as err:
    logger.error(str(err))
    sys.exit(1)

Base = declarative_base()

warnings.filterwarnings(
    "ignore",
    category=SAWarning,
    message=".*This declarative base already contains a class with the same class name and module name.*",
)


class BaseMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    updated_by = Column(UUID(as_uuid=True), nullable=True, unique=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_status = Column(Boolean(), default=False)
    deleted_at = Column(DateTime(), nullable=True)

    async def save(self, session: AsyncSession):
        session.add(self)
        await session.commit()

    async def update(self, session: AsyncSession, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        await session.commit()

    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.commit()

    @classmethod
    async def get(cls, session: AsyncSession, **kwargs):
        try:
            query = select(cls).filter_by(**kwargs, deleted_status=False)
            result = await session.scalar(query)
            return result
        except exc.NoResultFound:
            raise Exception("Data not found")

    @classmethod
    async def get_all(cls, session: AsyncSession):
        query = select(cls)
        result = await session.execute(query)
        return result.scalars().all()


def to_dict(instance, include_relationships: bool = True):
    """
    Convert SQLAlchemy ORM instance to dictionary.
    """
    try:

        def convert_value(value):
            if isinstance(value, list):
                return [
                    convert_value(item)
                    for item in value
                    if not hasattr(item, "deleted_status") or not item.deleted_status
                ]
            elif isinstance(value, dict):
                return {
                    key: convert_value(val)
                    for key, val in value.items()
                    if not hasattr(val, "deleted_status") or not val.deleted_status
                }
            else:
                return value

        data = {}
        for attr in class_mapper(instance.__class__).column_attrs:
            if attr.key == "deleted_status" and getattr(instance, attr.key):
                return {}  # Skip this instance if it is marked as deleted
            data[attr.key] = convert_value(getattr(instance, attr.key))

        if include_relationships:
            for attr in class_mapper(instance.__class__).relationships:
                relationship_value = getattr(instance, attr.key)
                if relationship_value is not None:
                    if isinstance(relationship_value, list):
                        data[attr.key] = [
                            convert_value(rel_instance)
                            for rel_instance in relationship_value
                            if not getattr(rel_instance, "deleted_status", False)
                        ]
                    elif isinstance(relationship_value, dict):
                        data[attr.key] = convert_value(relationship_value)
                    else:
                        if not getattr(relationship_value, "deleted_status", False):
                            data[attr.key] = convert_value(relationship_value)
                else:
                    data[attr.key] = None

        return data
    except Exception as e:
        logger.exception(f"Error while converting to dict: {e}")
        raise
