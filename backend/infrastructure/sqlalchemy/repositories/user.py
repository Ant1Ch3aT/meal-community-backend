from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.domain.entities.school_info import SchoolInfo
from backend.domain.entities.user import User
from backend.domain.repositories.user import UserRepository
from backend.infrastructure.sqlalchemy import SQLAlchemy
from backend.infrastructure.sqlalchemy.entities.school_info import SchoolInfoSchema
from backend.infrastructure.sqlalchemy.entities.user import UserSchema


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, sa: SQLAlchemy):
        self.sa = sa

    async def create(
        self, name: str, email: str, password: str, school_info: SchoolInfo
    ) -> User:
        async with self.sa.session_maker() as session:
            async with session.begin():
                user = UserSchema(
                    email=email,
                    password=password,
                    name=name,
                    school_info=SchoolInfoSchema.from_entity(school_info),
                )
                session.add(user)
            await session.commit()
            await user.awaitable_attrs.created_at
            return user.to_entity()

    async def get_id_by_email_with_password(
        self, email: str, password: str
    ) -> int | None:
        async with self.sa.session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(UserSchema)
                    .where(UserSchema.email == email, UserSchema.password == password)
                    .options(selectinload(UserSchema.school_info))
                )

                user = result.scalars().first()

                if user:
                    return user.id

    async def get_by_id(self, user_id: int) -> User:
        async with self.sa.session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(UserSchema)
                    .where(UserSchema.id == user_id)
                    .options(selectinload(UserSchema.school_info))
                )

                user = result.scalar_one()
                return user.to_entity()

    async def get_id_by_email(self, email: str) -> int | None:
        async with self.sa.session_maker() as session:
            async with session.begin():
                result = await session.execute(
                    select(UserSchema)
                    .where(UserSchema.email == email)
                    .options(selectinload(UserSchema.school_info))
                )

                user = result.scalars().first()

                if user:
                    return user.id
