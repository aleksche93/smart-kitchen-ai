import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Імпортуємо ваші моделі та додаток
from db.models import Base
from app import app, get_db

# 1. Налаштовуємо URL для тестової БД в пам'яті
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 2. Створюємо двигун один раз для всієї сесії тестів
@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Створюємо таблиці один раз
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield engine
    
    # Видаляємо таблиці після завершення всіх тестів
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

# 3. Фікстура для сесії БД: ізоляція через rollback
@pytest_asyncio.fixture()
async def db_session(engine):
    # Відкриваємо з'єднання та починаємо транзакцію
    async with engine.connect() as connection:
        transaction = await connection.begin()
        
        # Створюємо сесію, прив'язану до цього з'єднання
        async_session = async_sessionmaker(
            bind=connection, expire_on_commit=False
        )
        session = async_session()
        
        yield session
        
        # Після тесту закриваємо сесію і відкочуємо транзакцію (база знову чиста)
        await session.close()
        await transaction.rollback()

# 4. Фікстура для клієнта FastAPI
@pytest_asyncio.fixture()
async def client(db_session):
    # Оверрайд залежності БД
    app.dependency_overrides[get_db] = lambda: db_session
    
    # Використовуємо AsyncClient замість TestClient для повністю асинхронного бекенду
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
        
    # Очищуємо оверрайди після тесту
    app.dependency_overrides.clear()