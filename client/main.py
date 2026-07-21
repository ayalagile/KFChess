import asyncio
from client.network.network_client import NetworkClient

async def main():
    client = NetworkClient()
    try:
        await client.connect()
        
        listen_task = asyncio.create_task(client.listen())
        
        await client.send_message("ping", {"msg": "hello server"})
        
        await asyncio.sleep(1)
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())