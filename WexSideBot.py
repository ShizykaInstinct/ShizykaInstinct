import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telethon import TelegramClient, events
import asyncio

# ДАННЫЕ ДЛЯ ВХОДА
USERNAME = "Shizyka"  # Твой логин
PASSWORD = "freedcmnepoher1"  # Твой пароль
api_id = '29999608'  # твой API ID
api_hash = '96557fa849762e581db4427106a558d2'  # твой API hash
phone_number = '+17276362346'  # номер телефона для авторизации

# Функция для получения промокода
async def get_promo_code():
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start(phone_number)
    print("Telegram клиент авторизован!")

    promo_code = None  # Изначально промокод не найден

    # Функция для обработки новых сообщений
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        nonlocal promo_code  # Используем переменную promo_code, определённую в основном теле функции
        message = event.message.text
        print(f"Получено новое сообщение: {message}")
        # Ищем промокод, который начинается с WEX_ и состоит из букв и цифр, с дефисами
        match = re.search(r'WEX_[A-Za-z0-9-]+', message)
        if match:
            promo_code = match.group(0)
            print(f"Получен промокод: {promo_code}")
            await client.disconnect()  # Закрываем соединение после нахождения промокода

    print("Ожидаем сообщения с промокодом...")
    await client.run_until_disconnected()

    return promo_code

# Функция для выполнения работы
async def main():
    while True:  # Цикл, чтобы перезапускать процесс, если промокод неверный
        promo_code = await get_promo_code()  # Получаем промокод

        if not promo_code:
            print("❌ Не удалось получить промокод!")
            continue  # Пробуем снова, если промокод не найден

        print(f"Попытка ввести промокод: {promo_code}")

        # Настройки для запуска браузера в headless-режиме
        options = Options()
        options.add_argument('--headless')  # Запуск без графического интерфейса
        options.add_argument('--disable-gpu')  # Отключение GPU (не требуется в headless)
        options.add_argument('--no-sandbox')  # Отключение sandbox для работы в Termux
        options.add_argument('--disable-dev-shm-usage')  # Отключение использования /dev/shm

        # Путь к установленному Chromium (вы можете узнать его путь с помощью команды `which chromium`)
        chromium_path = '/data/data/com.termux/files/usr/bin/chromium'

        # Запуск Selenium с использованием Chromium
        driver = webdriver.Chrome(options=options, executable_path=chromium_path)

        driver.get("https://wexside.ru/login")  # Открываем сайт
        wait = WebDriverWait(driver, 20)  # Увеличиваем время ожидания

        start_time = time.time()

        try:
            # 1️⃣ Вводим логин
            username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Введите имя пользователя']")))
            username_input.send_keys(USERNAME)

            # 2️⃣ Вводим пароль
            password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Введите пароль']")))
            password_input.send_keys(PASSWORD)

            # 3️⃣ Нажимаем кнопку "Войти"
            login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='sc-DJfDf cfNroC btn btn-primary']")))
            login_button.click()

            # 4️⃣ Личный аакаунт
            profile_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='sc-fodVRF ZIMzY btn btn-outline-dark']")))
            profile_button.click()

            # 5️⃣ Нажимаем кнопку для открытия поля ввода промокода (по иконке)
            promo_code_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@style='background-color: rgb(17, 19, 23); border: 2px solid rgb(37, 39, 43); border-radius: 6px; margin-top: 1rem; width: 1.725rem; height: 1.725rem; display: flex; align-items: center; justify-content: center; cursor: pointer;']")))
            promo_code_button.click()

            # 6️⃣ Вводим текст в поле для промокода
            promo_code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='key']")))
            promo_code_input.send_keys(promo_code)

            # 7️⃣ Нажимаем кнопку "Отправить"
            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[style*='background-color: rgb(16, 19, 24)'] svg[data-icon='check']")))
            submit_button.click()
        except Exception as e:
            print(f"❌ Ошибка входа! Причина: {e}")
            driver.quit()
            continue  # Если ошибка, перезапускаем цикл

        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        print(f"✅ Скрипт выполнился за {execution_time:.2f} миллисекунд.")

        time.sleep(5)  # Оставляем браузер открытым на 5 секунд для проверки
        driver.quit()  # Закрываем браузер

        print("✅ Попытка завершена. Бот готов к следующей попытке.")
        time.sleep(10)  # Задержка перед повторной попыткой

# Запуск основного цикла
asyncio.run(main())