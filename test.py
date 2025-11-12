from sqlmodel import select

from authentication.core.database import db_manager
from authentication.models import Role


async def test_database_connection():
    db_manager.initialize()

    async with db_manager.get_session() as session:
        statement = select(Role)
        results = await session.execute(statement)
        role = results.scalar_one()

        print(role.permissions)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_database_connection())