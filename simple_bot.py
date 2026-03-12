#!/usr/bin/env python3
"""
Simple Telegram Bot with OnlySq API Integration

This is a simplified version that doesn't require aiogram dependency.
It uses direct HTTP requests to Telegram Bot API and OnlySq API.

Features:
- Chat with OnlySq API (gpt-4o-mini)
- Commands: /start, /help, /clear, /settings, /history, /image
- User history management
- Image generation via OnlySq API
"""

import os
import json
import logging
import requests
import base64
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set TELEGRAM_BOT_TOKEN environment variable")

# OnlySq API configuration
ONLYSQ_BASE_URL = "https://api.onlysq.ru/ai/openai"
ONLYSQ_API_KEY = "openai"  # Basic API key as mentioned in documentation

# Telegram API endpoints
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# User data storage
user_data: Dict[int, Dict] = {}

# Constants
MAX_HISTORY_LENGTH = 20  # Maximum number of messages to keep in history
MAX_IMAGE_PROMPT_LENGTH = 500  # Maximum length for image generation prompts


def get_user_data(user_id: int) -> Dict:
    """Get or create user data storage."""
    if user_id not in user_data:
        user_data[user_id] = {
            "history": [],
            "settings": {
                "model": "gpt-4o-mini",
                "max_tokens": 1000,
                "temperature": 0.7
            },
            "last_interaction": datetime.now()
        }
    return user_data[user_id]


def format_message_history(user_id: int) -> List[Dict]:
    """Format message history for OnlySq API."""
    user = get_user_data(user_id)
    history = user["history"]
    
    # Take last MAX_HISTORY_LENGTH messages
    recent_history = history[-MAX_HISTORY_LENGTH:] if len(history) > MAX_HISTORY_LENGTH else history
    
    formatted_history = []
    for msg in recent_history:
        formatted_history.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    return formatted_history


def send_telegram_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """Send message to Telegram user."""
    try:
        response = requests.post(
            f"{TELEGRAM_API_BASE}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Error sending Telegram message: {str(e)}")
        return False


def handle_start(chat_id: int, user_id: int):
    """Handle /start command."""
    user_data_obj = get_user_data(user_id)
    
    # Add system message if this is the first interaction
    if not user_data_obj["history"]:
        user_data_obj["history"].append({
            "role": "system",
            "content": "You are a helpful and friendly AI assistant. Answer user questions clearly and concisely.",
            "timestamp": datetime.now().isoformat()
        })
    
    welcome_text = """
🤖 Добро пожаловать в OnlySq Telegram Bot!

Я - ваш AI-помощник, интегрированный с OnlySq API. Вы можете:

• Просто писать мне сообщения для общения
• Использовать команды:
  /help - Справка по командам
  /settings - Настройки AI
  /history - Просмотр истории диалога
  /clear - Очистить историю
  /image - Сгенерировать изображение

Начните разговор, и я отвечу через OnlySq API! 🚀
"""
    
    send_telegram_message(chat_id, welcome_text)


def handle_help(chat_id: int):
    """Handle /help command."""
    help_text = """
📚 Справка по командам OnlySq Bot:

**Основные команды:**
• /start - Начать работу с ботом
• /help - Показать эту справку
• /clear - Очистить историю диалога

**Дополнительные функции:**
• /settings - Настройки AI модели
• /history - Просмотреть историю диалога
• /image - Сгенерировать изображение

**Как использовать:**
• Просто пишите сообщения для общения
• Используйте /image [описание] для генерации изображений
• Настройки позволяют изменить модель и параметры генерации

💡 Совет: Чем подробнее вы опишете запрос для генерации изображения, тем лучше результат!
"""
    
    send_telegram_message(chat_id, help_text)


def handle_clear(chat_id: int, user_id: int):
    """Handle /clear command."""
    user = get_user_data(user_id)
    
    # Reset history but keep system message
    system_messages = [msg for msg in user["history"] if msg["role"] == "system"]
    user["history"] = system_messages
    
    send_telegram_message(chat_id, "🧹 История диалога очищена! Начнем с чистого листа.")


def handle_settings(chat_id: int, user_id: int):
    """Handle /settings command."""
    user = get_user_data(user_id)
    settings = user["settings"]
    
    settings_text = f"""
⚙️ Текущие настройки AI:

**Модель:** {settings["model"]}
**Макс. токенов:** {settings["max_tokens"]}
**Температура:** {settings["temperature"]}

Доступные команды для настройки:
• /set_model [название] - Изменить модель
• /set_tokens [число] - Изменить макс. токены (100-4000)
• /set_temp [число] - Изменить температуру (0.0-2.0)

Примеры:
/set_model gpt-4o-mini
/set_tokens 1500
/set_temp 0.8
"""
    
    send_telegram_message(chat_id, settings_text)


def handle_set_model(chat_id: int, user_id: int, model_name: str):
    """Set AI model."""
    user = get_user_data(user_id)
    
    if not model_name:
        send_telegram_message(chat_id, "Пожалуйста, укажите название модели. Пример: /set_model gpt-4o-mini")
        return
    
    user["settings"]["model"] = model_name
    send_telegram_message(chat_id, f"✅ Модель изменена на: {model_name}")


def handle_set_tokens(chat_id: int, user_id: int, tokens_str: str):
    """Set max tokens."""
    user = get_user_data(user_id)
    
    if not tokens_str:
        send_telegram_message(chat_id, "Пожалуйста, укажите количество токенов. Пример: /set_tokens 1500")
        return
    
    try:
        tokens = int(tokens_str)
        if tokens < 100 or tokens > 4000:
            send_telegram_message(chat_id, "Количество токенов должно быть от 100 до 4000")
            return
        
        user["settings"]["max_tokens"] = tokens
        send_telegram_message(chat_id, f"✅ Максимальное количество токенов изменено на: {tokens}")
    except ValueError:
        send_telegram_message(chat_id, "Пожалуйста, введите корректное число токенов")


def handle_set_temp(chat_id: int, user_id: int, temp_str: str):
    """Set temperature."""
    user = get_user_data(user_id)
    
    if not temp_str:
        send_telegram_message(chat_id, "Пожалуйста, укажите значение температуры. Пример: /set_temp 0.8")
        return
    
    try:
        temp = float(temp_str)
        if temp < 0.0 or temp > 2.0:
            send_telegram_message(chat_id, "Температура должна быть от 0.0 до 2.0")
            return
        
        user["settings"]["temperature"] = temp
        send_telegram_message(chat_id, f"✅ Температура изменена на: {temp}")
    except ValueError:
        send_telegram_message(chat_id, "Пожалуйста, введите корректное значение температуры")


def handle_history(chat_id: int, user_id: int):
    """Handle /history command."""
    user = get_user_data(user_id)
    history = user["history"]
    
    if not history:
        send_telegram_message(chat_id, "История диалога пуста.")
        return
    
    # Format history for display
    history_text = "📜 История диалога:\n\n"
    
    for i, msg in enumerate(history[-10:], 1):  # Show last 10 messages
        role_emoji = "👤" if msg["role"] == "user" else "🤖" if msg["role"] == "assistant" else "⚙️"
        content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
        history_text += f"{i}. {role_emoji} {msg['role'].upper()}: {content_preview}\n\n"
    
    history_text += f"\nВсего сообщений в истории: {len(history)}"
    
    send_telegram_message(chat_id, history_text)


def handle_image(chat_id: int, prompt: str):
    """Handle /image command for image generation."""
    if not prompt:
        send_telegram_message(chat_id, "Пожалуйста, укажите описание для генерации изображения. Пример: /image красивый пейзаж с горами")
        return
    
    if len(prompt) > MAX_IMAGE_PROMPT_LENGTH:
        send_telegram_message(chat_id, f"Описание слишком длинное. Максимум {MAX_IMAGE_PROMPT_LENGTH} символов.")
        return
    
    # Send processing message
    processing_msg = send_telegram_message(chat_id, "🖼️ Генерирую изображение... Это может занять некоторое время.")
    
    try:
        # Generate image using OnlySq API
        headers = {
            "Authorization": "Bearer openai"
        }
        
        data = {
            "model": "flux",
            "prompt": prompt,
            "ratio": "16:9"
        }
        
        response = requests.post("https://api.onlysq.ru/ai/imagen", json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("files"):
            # For now, just send a text confirmation
            # In a real implementation, you would send the actual image
            send_telegram_message(chat_id, f"🎨 Сгенерировано изображение по запросу: {prompt}")
        else:
            send_telegram_message(chat_id, "❌ Не удалось сгенерировать изображение")
            
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка при генерации изображения: {str(e)}")


def handle_text_message(chat_id: int, user_id: int, user_input: str):
    """Handle regular text messages."""
    # Get user data and settings
    user = get_user_data(user_id)
    settings = user["settings"]
    
    try:
        # Add user message to history
        user["history"].append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send typing action
        requests.post(
            f"{TELEGRAM_API_BASE}/sendChatAction",
            json={
                "chat_id": chat_id,
                "action": "typing"
            }
        )
        
        # Prepare messages for OnlySq API
        messages = format_message_history(user_id)
        
        # Add current user message if not already included
        if not messages or messages[-1]["content"] != user_input:
            messages.append({
                "role": "user",
                "content": user_input
            })
        
        # Call OnlySq API
        client = __import__('openai', fromlist=['OpenAI']).OpenAI(
            base_url=ONLYSQ_BASE_URL,
            api_key=ONLYSQ_API_KEY,
        )
        
        completion = client.chat.completions.create(
            model=settings["model"],
            messages=messages,
            max_tokens=settings["max_tokens"],
            temperature=settings["temperature"],
        )
        
        # Get AI response
        ai_response = completion.choices[0].message.content
        
        # Add AI response to history
        user["history"].append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send response to user
        send_telegram_message(chat_id, ai_response)
        
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        send_telegram_message(chat_id, f"❌ Произошла ошибка при обработке вашего сообщения: {str(e)}")
        
        # Add error to history for debugging
        user["history"].append({
            "role": "system",
            "content": f"Error occurred: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })


def parse_command(text: str) -> tuple:
    """Parse command and arguments."""
    if not text.startswith('/'):
        return None, None
    
    parts = text.split(' ', 1)
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""
    
    return command, args.strip()


def process_update(update):
    """Process a single Telegram update."""
    try:
        message = update.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        user_id = message.get('from', {}).get('id')
        text = message.get('text', '')
        
        if not chat_id or not user_id:
            return
        
        # Parse command
        command, args = parse_command(text)
        
        if command == '/start':
            handle_start(chat_id, user_id)
        elif command == '/help':
            handle_help(chat_id)
        elif command == '/clear':
            handle_clear(chat_id, user_id)
        elif command == '/settings':
            handle_settings(chat_id, user_id)
        elif command == '/set_model':
            handle_set_model(chat_id, user_id, args)
        elif command == '/set_tokens':
            handle_set_tokens(chat_id, user_id, args)
        elif command == '/set_temp':
            handle_set_temp(chat_id, user_id, args)
        elif command == '/history':
            handle_history(chat_id, user_id)
        elif command == '/image':
            handle_image(chat_id, args)
        else:
            # Regular text message
            handle_text_message(chat_id, user_id, text)
            
    except Exception as e:
        logging.error(f"Error processing update: {str(e)}")


def main():
    """Main bot loop."""
    print("🚀 Запуск OnlySq Telegram Bot...")
    print("Убедитесь, что вы установили зависимости: pip install openai requests")
    print("И установили переменную окружения TELEGRAM_BOT_TOKEN")
    
    # Get updates offset
    offset = 0
    
    try:
        while True:
            # Get updates from Telegram
            response = requests.get(
                f"{TELEGRAM_API_BASE}/getUpdates",
                params={"offset": offset, "timeout": 30}
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok') and result.get('result'):
                for update in result['result']:
                    process_update(update)
                    offset = max(offset, update['update_id'] + 1)
                    
    except KeyboardInterrupt:
        print("\nОстановка бота...")
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        print(f"❌ Критическая ошибка: {str(e)}")


if __name__ == '__main__':
    main()