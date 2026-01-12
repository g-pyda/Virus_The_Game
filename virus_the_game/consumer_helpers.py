import httpx
import aioredis


# ----------------- API Interaction Helpers ----------------- #


async def get_api_data(
        endpoint: str,
        headers: dict = None,
        data: dict = None,
        timeout: int = 5
):
    """
    Perform an asynchronous GET request to the Django API.
    Constructs the full API URL and returns both status code and response data.

    Args:
        endpoint: API endpoint path (e.g., 'players/', 'games/123/')
        headers: Optional HTTP headers dictionary
        data: Optional query parameters or request data
        timeout: Request timeout in seconds (default: 5)

    Returns:
        Tuple of (status_code, response_json_dict)
    """
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
    """
    Perform an asynchronous POST request to the Django API.
    Used for creating new resources or submitting data to the backend.

    Args:
        endpoint: API endpoint path (e.g., 'players/', 'games/')
        headers: Optional HTTP headers dictionary
        data: Request payload to send in the POST body
        timeout: Request timeout in seconds (default: 5)

    Returns:
        Tuple of (status_code, response_json_dict)
    """
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
    """
    Perform an asynchronous DELETE request to the Django API.
    Used for removing resources from the backend.

    Args:
        endpoint: API endpoint path (e.g., 'players/123/', 'games/456/')
        headers: Optional HTTP headers dictionary
        data: Optional request data
        timeout: Request timeout in seconds (default: 5)

    Returns:
        Tuple of (status_code, response_json_dict)
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.delete(
            f"localhost:8000/api/{endpoint}",
            headers=headers,
            data=data
        )

        return response.status_code, response.json()


# ----------------- Redis Chanel Management ----------------- #


class RedisChannelManager:
    """
    Manages player and host channel names using Redis.
    Stores mapping of room_code -> player_id -> channel_name
    """

    def __init__(self, redis_connection):
        self.redis = redis_connection

    async def add_player(self, room_code, player_id, channel_name):
        """Register a player's channel name in Redis."""
        key = f"room:{room_code}:players"
        await self.redis.hset(key, player_id, channel_name)

    async def remove_player(self, room_code, player_id):
        """Unregister a player from Redis."""
        key = f"room:{room_code}:players"
        await self.redis.hdel(key, player_id)

    async def set_host(self, room_code, channel_name):
        """Register the host's channel name in Redis."""
        key = f"room:{room_code}:host"
        await self.redis.set(key, channel_name)

    async def remove_host(self, room_code):
        """Unregister the host from Redis."""
        key = f"room:{room_code}:host"
        await self.redis.delete(key)

    async def get_player_channel(self, room_code, player_id):
        """Get a specific player's channel name from Redis."""
        key = f"room:{room_code}:players"
        channel_name = await self.redis.hget(key, player_id)
        return channel_name.decode() if channel_name else None

    async def get_host_channel(self, room_code):
        """Get the host's channel name from Redis."""
        key = f"room:{room_code}:host"
        channel_name = await self.redis.get(key)
        return channel_name.decode() if channel_name else None

    async def get_all_players(self, room_code):
        """Get all players in a room from Redis."""
        key = f"room:{room_code}:players"
        players = await self.redis.hgetall(key)
        return {k.decode(): v.decode() for k, v in players.items()}

    async def get_room_participants(self, room_code):
        """Get all participants (players + host) from Redis."""
        return {
            'players': await self.get_all_players(room_code),
            'host': await self.get_host_channel(room_code)
        }

    async def cleanup_room(self, room_code):
        """Clean up all data for a room from Redis."""
        await self.redis.delete(f"room:{room_code}:players")
        await self.redis.delete(f"room:{room_code}:host")


async def get_redis_manager():
    """Get or create Redis connection for channel management."""
    redis = await aioredis.create_redis_pool('redis://redis:6379')
    return RedisChannelManager(redis)
