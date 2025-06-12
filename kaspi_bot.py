import requests
import os
import datetime
import json

print("🚀 KASPI BOT v3.7-safe-echo запущен")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
KASPI_API_URL = os.getenv("KASPI_API_URL")

def send_telegram(text):
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text}
        )
        print("📬 Telegram response:", response.status_code, response.text)
    except Exception as e:
        print("❌ Ошибка отправки в Telegram:", str(e))

def get_orders():
    try:
        print("🔄 Получаем данные от Kaspi...")
        response = requests.get(KASPI_API_URL)
        print("🧾 Ответ от Kaspi:", response.status_code)
        return response.json()
    except Exception as e:
        print("❌ Ошибка при получении заказов:", str(e))
        send_telegram(f"❌ Ошибка Kaspi API: {e}")
        return {}

def main():
    try:
        orders_data = get_orders()
        orders = orders_data.get("orders", [])

        now = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")

        if not orders:
            msg = f"❌ [v3.7] Нет заказов. Время: {time_str}"
            print(msg)
            send_telegram(msg)
        else:
            preview = json.dumps(orders[:2], indent=2, ensure_ascii=False)
            print("📦 Есть заказы:", preview)
            send_telegram(f"✅ Заказы: {len(orders)}\n<pre>{preview}</pre>")

    except Exception as e:
        print("❌ Общая ошибка:", str(e))
        send_telegram(f"❌ Ошибка в main(): {e}")

if __name__ == "__main__":
    main()
