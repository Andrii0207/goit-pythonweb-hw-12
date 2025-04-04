"""
Utils API
=========

This module provides utility endpoints for system health checking.

Endpoints:
    - `/healthchecker` (GET): Check the database connection and return system status.

"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db

router = APIRouter(tags=["utils"])

@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
       Check the database connection and return system status.

       :param db: Database session.
       :type db: AsyncSession
       :return: A message indicating the system status.
       :rtype: dict
       :raises HTTPException: If the database is not configured correctly or there is an error connecting.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )
