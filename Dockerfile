FROM python:3.12-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл залежностей спочатку (для оптимізації кешу Docker)
COPY requirements.txt .

# Оновлюємо pip та встановлюємо залежності без використання кешу, щоб зменшити розмір образу
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копіюємо весь решту коду до контейнера
COPY . .

# Відкриваємо порт 8000 для зовнішнього доступу до FastAPI
EXPOSE 8000

# Запускаємо uvicorn сервер на хості 0.0.0.0
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
