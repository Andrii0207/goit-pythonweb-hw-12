"""
Database Module
===============

This module handles database connections using SQLAlchemy with asynchronous support.

Classes:
    - `DatabaseSessionManager`: Manages database sessions and connections.

Functions:
    - `get_db()`: Provides an asynchronous database session generator.

"""

import contextlib
from typing import Union

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
        Manages the database connection and provides session handling.

        :param url: The database connection URL.
        :type url: str
    """
    def __init__(self, url: str):
        self._engine: Union[AsyncEngine, None] = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
              Provides an asynchronous database session.

              :raises Exception: If the session manager is not initialized.
              :raises SQLAlchemyError: If a database error occurs.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(settings.DB_URL)

async def get_db():
    """
       Dependency function that provides a new asynchronous database session.

       :yield: A database session.
    """
    async with sessionmanager.session() as session:
        yield session
