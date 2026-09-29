from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# URL limpia sin parámetros extra en la cadena de texto
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_oKOviPm7NJD6@ep-fragrant-night-b4urr32p-pooler.c-6.us-east-2.aws.neon.tech/neondb"

# Configuramos el SSL directamente en connect_args para evitar cualquier conflicto
engine = create_async_engine(
    DATABASE_URL, 
    connect_args={"ssl": "require"},
    echo=True, 
    future=True
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with async_session_maker() as session:
        yield session