import httpx


async def get_api_data(
        endpoint: str,
        headers: dict = None,
        data: dict = None,
        timeout: int = 5
):

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(
            f"localhost:8000/api/{endpoint}",
            headers=headers,
            data=data
        )

        return response.status_code, response.json()


async def post_api_data(
        endpoint: str,
        headers: dict = None,
        data: dict = None,
        timeout: int = 5
):

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"localhost:8000/api/{endpoint}",
            headers=headers,
            data=data
        )

        return response.status_code, response.json()


async def delete_api_data(
        endpoint: str,
        headers: dict = None,
        data: dict = None,
        timeout: int = 5
):

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.delete(
            f"localhost:8000/api/{endpoint}",
            headers=headers,
            data=data
        )

        return response.status_code, response.json()
