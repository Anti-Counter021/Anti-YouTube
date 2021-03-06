from typing import List, Optional, Generic, TypeVar, Type

import sqlalchemy
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, delete, update, exists
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar('ModelType', bound=sqlalchemy.Table)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """ Base CRUD """

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def filter(self, db: AsyncSession, **kwargs) -> List[ModelType]:
        """
            Filter
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: Models
            :rtype: list
        """
        query = await db.execute(select(self.model).order_by(self.model.id.desc()).filter_by(**kwargs))
        return query.scalars()

    async def get(self, db: AsyncSession,  **kwargs) -> Optional[ModelType]:
        """
            Get
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: Model
            :rtype: ModelType
        """
        query = await db.execute(select(self.model).filter_by(**kwargs))
        return query.scalars().first()

    async def exists(self,  db: AsyncSession, **kwargs) -> bool:
        """
            Exists
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: Exists?
        """
        query = await db.execute(exists(select(self.model.id).filter_by(**kwargs)).select())
        return query.scalar()

    async def page_exists(self, db: AsyncSession, skip: int, limit: int):
        """
            Next query exists?
            :param db: DB
            :type db: AsyncSession
            :param skip: Skip
            :type skip: int
            :param limit: Limit
            :type limit: int
            :return: Page exists?
        """
        query = await db.execute(exists(select(self.model).order_by(self.model.id.desc()).offset(skip).limit(limit)).select())
        return query.scalar()

    async def all(self, db: AsyncSession,  skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
            All
            :param db: DB
            :type db: AsyncSession
            :param skip: start
            :type skip: int
            :param limit: end
            :type limit: int
            :return: All ModelType
            :rtype: list
        """
        query = await db.execute(select(self.model).order_by(self.model.id.desc()).offset(skip).limit(limit))
        return query.scalars().all()

    async def create(self, db: AsyncSession,  schema: CreateSchemaType, **kwargs) -> ModelType:
        """
            Create
            :param db: DB
            :type db: AsyncSession
            :param schema: data
            :type schema: CreateSchemaType
            :param kwargs: kwargs
            :return: New model
            :rtype: ModelType
        """
        data = jsonable_encoder(schema)
        obj = self.model(**{**data, **kwargs})
        db.add(obj)
        await db.flush()
        return await self.get(db, id=obj.id)

    async def remove(self, db: AsyncSession, **kwargs) -> None:
        """
            Remove
            :param db: DB
            :type db: AsyncSession
            :param kwargs: kwargs
            :return: None
        """
        await db.execute(delete(self.model).filter_by(**kwargs))

    async def update(self, db: AsyncSession,  pk: int, schema: UpdateSchemaType, **kwargs) -> ModelType:
        """
            Update
            :param db: DB
            :type db: AsyncSession
            :param pk: ID
            :type pk: int
            :param schema: Update data
            :type schema: UpdateSchemaType
            :param kwargs: kwargs
            :return: Updated model
            :rtype: ModelType
        """
        update_data = {**schema.dict(skip_defaults=False), **kwargs}
        query = update(self.model).filter(self.model.id == pk).values(**update_data)
        query.execution_options(synchronize_session="fetch")
        await db.execute(query)
        return await self.get(db, id=pk)
