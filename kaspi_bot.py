
import os
import requests
import pytz
from datetime import datetime

# Настройки
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Версия бота
BOT_VERSION = "v4.0"

# Kaspi API URL
KASPI_API_URL = "https://kaspi.kz/shop/api/orders"

# Заголовки с куками
headers = {
    "X-Mc-Api-Session-Id": "Y4-1c639cc5-583e-47f7-98ac-e6f5e0f80aac",
    "Cookie": (
        "kaspi.storefront.cookie.city=750000000; "
        "mc-sid=1d86f21b-fa72-4f74-bf9f-67847b5eccdd; "
        "ssaid=79a7e9b0-998d-11ee-9a95-77ef56f38499; "
        "ks.tg=15"
    )
}

# Получение заказов
def get_orders():
    try:
        response = requests.get(KASPI_API_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"❌ Ошибка Kaspi API: {e}"

# Отправка сообщения в Telegram
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

def main():
    print(f"🚀 KASPI BOT {BOT_VERSION} запущен")
    print("🔄 Получаем данные от Kaspi...")

    result = get_orders()

    # Время в часовом поясе Алматы
    tz = pytz.timezone('Asia/Almaty')
    current_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

    if isinstance(result, str):
        send_telegram_message(result)
    elif result and isinstance(result, dict) and result.get("orders"):
        orders = result["orders"]
        message = f"📦 Найдено заказов: {len(orders)}. Время: {current_time}"
        send_telegram_message(message)
    else:
        send_telegram_message(f"❌ [{BOT_VERSION}] Нет заказов. Время: {current_time}")

if __name__ == "__main__":
    main()
