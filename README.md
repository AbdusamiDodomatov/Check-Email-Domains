 MX Checker Telegram Bot

Простой инструмент для проверки MX-записей email-адресов с интеграцией в Telegram.  

- Получает список email из сообщений Telegram  
- Проверяет наличие MX-записей домена  
- Отправляет результат обратно в тот же чат  

---

 Содержание проекта

- `mx_check_bot.py` — основной скрипт бота  
- `requirements.txt` — список зависимостей (если нужно)  
- Пример: `message.txt` (для локального теста, необязательно)  

---

 Установка и запуск

1. Клонируем или скачиваем проект.  
2. Создаём виртуальное окружение:

```cmd
python -m venv venv
venv\Scripts\activate

3. Устанавливаем зависимости:

pip install dnspython requests

4. Открываем mx_check_bot.py и вставляем свой Telegram Bot Token:

TG_BOT_TOKEN = "ВАШ_BOT_TOKEN"

5. Запускаем бота:

python mx_check_bot.py


