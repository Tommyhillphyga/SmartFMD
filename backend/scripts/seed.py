import asyncio

from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.services.seed import seed_database


async def main() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        result = await seed_database(session)
    print("Seed completed:", result)


if __name__ == "__main__":
    asyncio.run(main())

