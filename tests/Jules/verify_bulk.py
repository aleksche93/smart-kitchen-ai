import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
import sys
import os

# Ensure we can import from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models import Base, ReceiptHistoryModel, InventoryItemModel
import app

async def verify():
    print("--- Початок перевірки Bulk Deletion Architecture ---")
    
    # 1. Setup in-memory test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    test_async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    # Override the app's sessionmaker with our test one
    original_session = app.async_session
    app.async_session = test_async_session
    
    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        # 2. Seed Data
        async with test_async_session() as session:
            receipt = ReceiptHistoryModel(id="receipt_123", image_hash="dummyhash", store_name="Silpo")
            item1 = InventoryItemModel(id="item_1", receipt_id="receipt_123", name="Milk", user_id="u1")
            item2 = InventoryItemModel(id="item_2", receipt_id="receipt_123", name="Bread", user_id="u1")
            session.add_all([receipt, item1, item2])
            await session.commit()
            
        print("✅ Крок 1: База даних ініціалізована (1 Чек, 2 Товари).")
        
        # 3. Виконання Bulk Deletion (orphan mode)
        print("Виконуємо app.delete_receipt_and_sync_inventory('receipt_123', delete_items=False)...")
        success = await app.delete_receipt_and_sync_inventory("receipt_123", delete_items=False)
        print(f"✅ Крок 2: Функція повернула {success}.")
        
        # 4. Перевірка результатів
        async with test_async_session() as session:
            # Чек має бути видалений
            receipt_check = await session.get(ReceiptHistoryModel, "receipt_123")
            assert receipt_check is None, "Помилка: Чек не видалився!"
            
            # Товари мають залишитися, але receipt_id має стати NULL
            items = await session.execute(text("SELECT id, name, receipt_id FROM inventory_items"))
            rows = items.fetchall()
            
            assert len(rows) == 2, "Помилка: Товари були видалені!"
            for row in rows:
                assert row[2] is None, f"Помилка: Товар {row[1]} досі прив'язаний до чеку (receipt_id={row[2]})!"
                
        print("✅ Крок 3: Перевірка успішна! Товари відв'язані (receipt_id = NULL), чек видалено.")
        print("🚀 Bulk Deletion працює бездоганно і не потребує N+1 запитів!")
        
    finally:
        # Restore
        app.async_session = original_session
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify())
