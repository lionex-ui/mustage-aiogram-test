import httpx

from src.config import host_config
from src.utils import logging


async def get_expenses(params: dict) -> list[dict]:
    try:
        async with httpx.AsyncClient(base_url=host_config.host, http2=True, timeout=10) as client:
            response = await client.get("/expenses", params=params)
    except httpx.ConnectError:
        return []

    logging.logger.info(f"GET: {str(response.json())}")
    return response.json()


async def add_expense(json: dict) -> int:
    try:
        async with httpx.AsyncClient(base_url=host_config.host, http2=True, timeout=10) as client:
            response = await client.post("/expenses", json=json)
    except httpx.ConnectError:
        return 500

    logging.logger.info(f"ADD: {str(response.json())}")
    return response.status_code


async def edit_expense(json: dict) -> int:
    try:
        async with httpx.AsyncClient(base_url=host_config.host, http2=True, timeout=10) as client:
            response = await client.put("/expenses", json=json)
    except httpx.ConnectError:
        return 500

    logging.logger.info(f"EDIT: {str(response.json())}")
    return response.status_code


async def delete_expense(expense_id: int) -> int:
    try:
        async with httpx.AsyncClient(base_url=host_config.host, http2=True, timeout=10) as client:
            response = await client.delete(f"/expenses/{expense_id}")
    except httpx.ConnectError:
        return 500

    logging.logger.info(f"DELETE: {str(response.json())}")
    return response.status_code
