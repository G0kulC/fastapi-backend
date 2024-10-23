import datetime
from api.logging_config import setup_logging
from sqlalchemy import desc
from sqlalchemy import Column, String, inspect
from api.models import BaseMixin, Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logger = setup_logging(__name__)


def MymodelModel(schema_name):
    class Mymodel(Base, BaseMixin):
        __tablename__ = "mymodel"
        __table_args__ = {"schema": schema_name, "extend_existing": True}

        column = Column(String(), nullable=False, unique=False)
        # Rest of columns

        def to_dict(self):
            return {
                c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
            }

        @classmethod
        async def get(cls, session: AsyncSession, **kwargs):
            try:
                query = select(cls).filter_by(**kwargs, deleted_status=False)
                result = await session.scalar(query)
                if result is None:
                    raise Exception("Data not found")
                return result
            except Exception as e:
                logger.error(e)
                raise Exception("Data not found")

        @classmethod
        async def get_all(cls, session: AsyncSession):
            try:
                base_query = select(cls).filter_by(deleted_status=False)
                sort_query = base_query.order_by(desc(cls.updated_at))
                query_items = await session.scalars(sort_query)
                result = query_items.all()
                return result
            except Exception as e:
                logger.error(e)
                raise Exception("Data not found")

        @classmethod
        async def update(cls, session: AsyncSession, updated_data: dict, id=None):
            try:
                query = select(cls).filter(cls.id == id, cls.deleted_status == False)
                item = await session.scalar(query)
                if not item:
                    logger.debug("Data not found")
                    raise Exception("Data not found")
                logger.debug(f"Result {item}")
                for key, value in updated_data.items():
                    setattr(item, key, value)
                await session.commit()
                return item
            except Exception as e:
                await session.rollback()
                logger.error(f"Error occurred updating Data: {e}")
                raise Exception("Data not found")

        @classmethod
        async def delete(cls, session: AsyncSession, id=None, updated_by=None):
            try:
                query = select(cls).filter(cls.id == id, cls.deleted_status == False)
                item = await session.scalar(query)
                if not item:
                    logger.debug("Data not found")
                    raise Exception("Data not found")
                item.updated_by = updated_by
                item.deleted_status = True
                item.deleted_at = datetime.datetime.now()
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Error occurred deleting Data: {e}")
                raise Exception("Data not found")

    return Mymodel
