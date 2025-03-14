import httpx
import asyncio
import time

async def main():
    url = "https://www.example.com"
    start_time = time.monotonic()
    
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for _ in range(10)]
        responses = await asyncio.gather(*tasks)
    total_duration = time.monotonic() - start_time
    print(f"Total execution time: {total_duration:.4f} seconds")

asyncio.run(main())