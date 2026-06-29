import os

import pandas as pd
import gspread

from dotenv import load_dotenv
from sqlalchemy import create_engine

from google.oauth2.service_account import Credentials


# =====================================================
# Загрузка переменных окружения
# =====================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")


# =====================================================
# Подключение к PostgreSQL
# =====================================================

DATABASE_URL = (
    f"postgresql://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# =====================================================
# SQL-запрос
# =====================================================

query = """
SELECT *
FROM trades;
"""


# =====================================================
# EXTRACT
# Получение данных из PostgreSQL
# =====================================================

print("Получение данных из PostgreSQL...")

df = pd.read_sql(query, engine)

print(f"Получено строк: {len(df)}")


# =====================================================
# TRANSFORM
# Преобразование данных
# =====================================================

print("Преобразование данных...")

# df["last_order_date"] = pd.to_datetime(
#     df["last_order_date"]
# )
#
# df["days_since_order"] = (
#     pd.Timestamp.now()
#     - df["last_order_date"]
# ).dt.days
#
# df["customer_name"] = (
#     df["customer_name"]
#     .str.strip()
#     .str.title()
# )

print("Преобразование завершено")


# =====================================================
# Подключение к Google Sheets
# =====================================================

print("Подключение к Google Sheets...")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_file(
    "service_account.json",
    scopes=SCOPES
)
print("Sheet ID:", GOOGLE_SHEET_ID)
print("Service account:", credentials.service_account_email)

client = gspread.authorize(credentials)

for sheet in client.openall():
    print(sheet.title)

spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)

worksheet = spreadsheet.worksheet(
    "Import"
)


# =====================================================
# LOAD
# Полное обновление листа Import
# =====================================================

print("Обновление Google Sheets...")

worksheet.clear()

# Преобразовать все datetime-колонки в строки
for col in df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
    df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

data = [df.columns.tolist()] + df.values.tolist()

worksheet.update(data)

print("Google Sheets успешно обновлен")


# =====================================================
# Завершение
# =====================================================

print("ETL выполнен успешно")