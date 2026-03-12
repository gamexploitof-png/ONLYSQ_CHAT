#!/usr/bin/env python3
"""
Пример использования OnlySq API напрямую (без Telegram бота)

Этот скрипт демонстрирует, как можно использовать OnlySq API
для генерации текста и других задач.
"""

import os
from openai import OpenAI

# Настройка OnlySq API
client = OpenAI(
    base_url="https://api.onlysq.ru/ai/openai",
    api_key="openai",  # Базовый API ключ
)

def chat_with_onlysq():
    """Пример чата с OnlySq API."""
    print("🤖 Добро пожаловать в OnlySq AI Chat!")
    print("Введите 'exit' для выхода\n")
    
    # История диалога
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and friendly AI assistant. Answer user questions clearly and concisely."
        }
    ]
    
    while True:
        user_input = input("Вы: ")
        
        if user_input.lower() == 'exit':
            print("До свидания! 🚀")
            break
        
        if not user_input.strip():
            continue
        
        # Добавляем сообщение пользователя
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        try:
            # Отправляем запрос в OnlySq API
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            
            # Получаем ответ
            ai_response = completion.choices[0].message.content
            
            # Добавляем ответ в историю
            messages.append({
                "role": "assistant",
                "content": ai_response
            })
            
            print(f"AI: {ai_response}\n")
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}\n")

def generate_text_example():
    """Пример генерации текста по промпту."""
    prompt = "Напиши короткое эссе о важности искусственного интеллекта в современном мире."
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional writer. Create high-quality content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1500,
            temperature=0.8,
        )
        
        response = completion.choices[0].message.content
        print("📝 Сгенерированный текст:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Ошибка генерации: {str(e)}")

def summarize_text_example():
    """Пример суммаризации текста."""
    long_text = """
    Искусственный интеллект (ИИ) — это область компьютерных наук, занимающаяся созданием систем, 
    способных выполнять задачи, которые обычно требуют человеческого интеллекта. 
    Эти задачи включают в себя распознавание речи, визуальное восприятие, принятие решений и перевод текста.
    
    Современный ИИ основан на различных технологиях, включая машинное обучение, глубокое обучение и нейронные сети. 
    Машинное обучение позволяет системам автоматически улучшаться на основе опыта, 
    а глубокое обучение использует многослойные нейронные сети для анализа сложных данных.
    
    ИИ находит применение во многих сферах: медицине, финансах, транспорте, образовании и развлечениях. 
    В медицине ИИ помогает в диагностике заболеваний, в финансах — в прогнозировании рынков, 
    в транспорте — в разработке автономных автомобилей.
    
    Несмотря на успехи, ИИ сталкивается с этическими и социальными вызовами, 
    такими как вопросы приватности, предвзятости алгоритмов и влияние на занятость.
    """
    
    prompt = f"Суммаризируй следующий текст до 3-4 предложений:\n\n{long_text}"
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.3,
        )
        
        summary = completion.choices[0].message.content
        print("📋 Суммаризация текста:")
        print("=" * 30)
        print(summary)
        print("=" * 30)
        
    except Exception as e:
        print(f"❌ Ошибка суммаризации: {str(e)}")

def code_explanation_example():
    """Пример объяснения кода."""
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Пример использования
for i in range(10):
    print(fibonacci(i))
"""
    
    prompt = f"Объясни, что делает следующий код на Python:\n\n{code}"
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.5,
        )
        
        explanation = completion.choices[0].message.content
        print("💻 Объяснение кода:")
        print("=" * 40)
        print(explanation)
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Ошибка объяснения: {str(e)}")

def image_generation_example():
    """Пример генерации изображений через OnlySq API."""
    import requests
    import base64
    
    # Настройка заголовков
    headers = {
        "Authorization": "Bearer openai"
    }
    
    # Параметры генерации
    data = {
        "model": "flux",
        "prompt": "красивый пейзаж с горами и озером, реалистичный стиль",
        "ratio": "16:9"
    }
    
    try:
        print("🖼️ Генерация изображения через OnlySq API...")
        response = requests.post("https://api.onlysq.ru/ai/imagen", json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Изображение сгенерировано!")
        print(f"ID: {result['id']}")
        print(f"Время генерации: {result['elapsed-time']:.2f} секунд")
        print(f"Размер: {result['size']}")
        
        # Сохранение изображения
        if result.get("files"):
            image_data = base64.b64decode(result["files"][0])
            filename = f"generated_image_{result['id'][:8]}.png"
            
            with open(filename, "wb") as f:
                f.write(image_data)
            
            print(f"🖼️ Изображение сохранено как: {filename}")
        
    except Exception as e:
        print(f"❌ Ошибка генерации изображения: {str(e)}")


def cloud_storage_example():
    """Пример использования OnlySq Cloud для загрузки файлов."""
    import requests
    import os
    
    print("☁️ Пример использования OnlySq Cloud")
    print("Для этого примера нужен реальный файл для загрузки")
    
    # Пример создания тестового файла
    test_filename = "test_file.txt"
    with open(test_filename, "w", encoding="utf-8") as f:
        f.write("Это тестовый файл для демонстрации OnlySq Cloud\n")
        f.write(f"Время создания: {datetime.now()}\n")
        f.write("OnlySq Cloud - быстрое и надежное облачное хранилище!\n")
    
    try:
        print(f"📤 Загрузка файла {test_filename} в OnlySq Cloud...")
        
        with open(test_filename, "rb") as f:
            files = {"file": (test_filename, f, "text/plain")}
            response = requests.post("https://cloud.onlysq.ru/upload", files=files)
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                print(f"✅ Файл успешно загружен!")
                print(f"Владелец: {result['owner']}")
                print(f"Ссылка для скачивания: {result['url']}")
            else:
                print(f"❌ Ошибка загрузки: {result}")
                
    except Exception as e:
        print(f"❌ Ошибка загрузки в облако: {str(e)}")
    
    finally:
        # Удаление тестового файла
        if os.path.exists(test_filename):
            os.remove(test_filename)


def api20_example():
    """Пример использования API2.0 напрямую."""
    import requests
    
    print("🌐 Пример использования API2.0")
    
    # Настройка заголовков
    headers = {
        "Authorization": "Bearer openai"
    }
    
    # Параметры запроса
    data = {
        "model": "gemini-2.5-flash",
        "request": {
            "messages": [
                {
                    "role": "user",
                    "content": "Расскажи о преимуществах использования OnlySq API"
                }
            ]
        }
    }
    
    try:
        print("📤 Отправка запроса через API2.0...")
        response = requests.post("https://api.onlysq.ru/ai/v2", json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Ответ получен!")
        print(f"ID: {result['id']}")
        print(f"Модель: {result['model']}")
        print(f"Токены: {result['usage']}")
        print("\n📝 Ответ:")
        print("=" * 50)
        print(result['choices'][0]['message']['content'])
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Ошибка API2.0: {str(e)}")


def main():
    """Главная функция с выбором примеров."""
    print("🎯 Примеры использования OnlySq API")
    print("=" * 50)
    
    examples = {
        "1": ("Чат с AI", chat_with_onlysq),
        "2": ("Генерация текста", generate_text_example),
        "3": ("Суммаризация текста", summarize_text_example),
        "4": ("Объяснение кода", code_explanation_example),
        "5": ("Генерация изображений", image_generation_example),
        "6": ("OnlySq Cloud", cloud_storage_example),
        "7": ("API2.0", api20_example),
    }
    
    while True:
        print("\nВыберите пример:")
        for key, (name, _) in examples.items():
            print(f"{key}. {name}")
        print("0. Выход")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "0":
            print("До свидания! 🚀")
            break
        elif choice in examples:
            print(f"\n🔧 Запуск: {examples[choice][0]}")
            print("-" * 50)
            examples[choice][1]()
            print("-" * 50)
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
