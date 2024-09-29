# Вказуємо базовий образ з необхідною версією Python
FROM python:3.11-slim

# Встановлюємо змінну середовища для запобігання створенню .pyc файлів
ENV PYTHONDONTWRITEBYTECODE=1

# Встановлюємо змінну середовища для буфера вводу/виводу
ENV PYTHONUNBUFFERED=1

# Встановлюємо pipenv
RUN pip install --upgrade pip
RUN pip install pipenv

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо Pipfile та Pipfile.lock до контейнера
COPY Pipfile Pipfile.lock /app/

# Встановлюємо залежності
RUN pipenv install --deploy --ignore-pipfile

# Копіюємо весь проект до контейнера
COPY . /app/

# Вказуємо команду за замовчуванням для запуску застосунку
CMD ["pipenv", "run", "python", "main.py"]