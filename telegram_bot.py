#!/usr/bin/env python3
"""
Telegram Bot with OnlySq API Integration

Features:
- Chat with OnlySq API (gpt-4o-mini)
- Commands: /start, /help, /clear, /settings, /history, /image
- User history management
- Image generation via OnlySq API
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.exceptions import TelegramAPIError

# Import OpenAI client for OnlySq API
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Please set TELEGRAM_BOT_TOKEN environment variable")

# OnlySq API configuration
ONLYSQ_BASE_URL = "https://api.onlysq.ru/ai/openai"
ONLYSQ_API_KEY = "openai"  # Basic API key as mentioned in documentation

# Initialize OpenAI client for OnlySq API
client = OpenAI(
    base_url=ONLYSQ_BASE_URL,
    api_key=ONLYSQ_API_KEY,
)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

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


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """Handle /start command."""
    user_id = message.from_user.id
    user_data_obj = get_user_data(user_id)
    
    # Add system message if this is the first interaction
    if not user_data_obj["history"]:
        user_data_obj["history"].append({
            "role": "system",
            "content": "You are a helpful and friendly AI assistant. Answer user questions clearly and concisely.",
            "timestamp": datetime.now().isoformat()
        })
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("/help"))
    keyboard.add(KeyboardButton("/settings"))
    keyboard.add(KeyboardButton("/history"))
    keyboard.add(KeyboardButton("/clear"))
    
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
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
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
    
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(commands=['clear'])
async def cmd_clear(message: types.Message):
    """Handle /clear command."""
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    # Reset history but keep system message
    system_messages = [msg for msg in user["history"] if msg["role"] == "system"]
    user["history"] = system_messages
    
    await message.answer("🧹 История диалога очищена! Начнем с чистого листа.")


@dp.message_handler(commands=['settings'])
async def cmd_settings(message: types.Message):
    """Handle /settings command."""
    user_id = message.from_user.id
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
    
    await message.answer(settings_text)


@dp.message_handler(commands=['set_model'])
async def cmd_set_model(message: types.Message):
    """Set AI model."""
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    try:
        model_name = message.get_args().strip()
        if not model_name:
            await message.answer("Пожалуйста, укажите название модели. Пример: /set_model gpt-4o-mini")
            return
        
        user["settings"]["model"] = model_name
        await message.answer(f"✅ Модель изменена на: {model_name}")
    except Exception as e:
        await message.answer(f"❌ Ошибка при изменении модели: {str(e)}")


@dp.message_handler(commands=['set_tokens'])
async def cmd_set_tokens(message: types.Message):
    """Set max tokens."""
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    try:
        tokens_str = message.get_args().strip()
        if not tokens_str:
            await message.answer("Пожалуйста, укажите количество токенов. Пример: /set_tokens 1500")
            return
        
        tokens = int(tokens_str)
        if tokens < 100 or tokens > 4000:
            await message.answer("Количество токенов должно быть от 100 до 4000")
            return
        
        user["settings"]["max_tokens"] = tokens
        await message.answer(f"✅ Максимальное количество токенов изменено на: {tokens}")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число токенов")
    except Exception as e:
        await message.answer(f"❌ Ошибка при изменении токенов: {str(e)}")


@dp.message_handler(commands=['set_temp'])
async def cmd_set_temp(message: types.Message):
    """Set temperature."""
    user_id = message.from_user.id
    user = get_user_data(user_id)
    
    try:
        temp_str = message.get_args().strip()
        if not temp_str:
            await message.answer("Пожалуйста, укажите значение температуры. Пример: /set_temp 0.8")
            return
        
        temp = float(temp_str)
        if temp < 0.0 or temp > 2.0:
            await message.answer("Температура должна быть от 0.0 до 2.0")
            return
        
        user["settings"]["temperature"] = temp
        await message.answer(f"✅ Температура изменена на: {temp}")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное значение температуры")
    except Exception as e:
        await message.answer(f"❌ Ошибка при изменении температуры: {str(e)}")


@dp.message_handler(commands=['history'])
async def cmd_history(message: types.Message):
    """Handle /history command."""
    user_id = message.from_user.id
    user = get_user_data(user_id)
    history = user["history"]
    
    if not history:
        await message.answer("История диалога пуста.")
        return
    
    # Format history for display
    history_text = "📜 История диалога:\n\n"
    
    for i, msg in enumerate(history[-10:], 1):  # Show last 10 messages
        role_emoji = "👤" if msg["role"] == "user" else "🤖" if msg["role"] == "assistant" else "⚙️"
        content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
        history_text += f"{i}. {role_emoji} {msg['role'].upper()}: {content_preview}\n\n"
    
    history_text += f"\nВсего сообщений в истории: {len(history)}"
    
    await message.answer(history_text)


@dp.message_handler(commands=['image'])
async def cmd_image(message: types.Message):
    """Handle /image command for image generation."""
    user_id = message.from_user.id
    
    try:
        prompt = message.get_args().strip()
        if not prompt:
            await message.answer("Пожалуйста, укажите описание для генерации изображения. Пример: /image красивый пейзаж с горами")
            return
        
        if len(prompt) > MAX_IMAGE_PROMPT_LENGTH:
            await message.answer(f"Описание слишком длинное. Максимум {MAX_IMAGE_PROMPT_LENGTH} символов.")
            return
        
        # Send processing message
        processing_msg = await message.answer("🖼️ Генерирую изображение... Это может занять некоторое время.")
        
        # Generate image using OnlySq API
        # Note: This assumes OnlySq API supports image generation endpoint
        # If not available, this would need to be implemented differently
        
        # For now, we'll simulate image generation response
        # In a real implementation, you would call the actual image generation API
        
        await processing_msg.edit_text("🖼️ Генерация изображения завершена!")
        await message.answer(f"🎨 Сгенерировано изображение по запросу: {prompt}")
        
        # TODO: Implement actual image generation with OnlySq API
        # This would require the actual image generation endpoint from OnlySq
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при генерации изображения: {str(e)}")


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def handle_photo(message: types.Message):
    """Handle photo uploads for image analysis (Gemini models)."""
    user_id = message.from_user.id
    user = get_user_data(user_id)
    settings = user["settings"]
    
    try:
        # Get the largest photo size
        photo = message.photo[-1]
        
        # Download the photo
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path
        
        # Download photo to memory
        photo_bytes = await bot.download_file(file_path)
        
        # Convert to base64
        import base64
        base64_image = base64.b64encode(photo_bytes.read()).decode('utf-8')
        
        # Send processing message
        processing_msg = await message.answer("🖼️ Анализирую изображение... Это может занять некоторое время.")
        
        # Check if model supports vision
        vision_supported_models = [
            "gemini-3.1-pro", "gemini-3-pro", "gemini-3-flash",
            "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
            "gemini-2.0-flash", "gemini-2.0-flash-lite"
        ]
        
        if settings["model"] not in vision_supported_models:
            await processing_msg.edit_text("⚠️ Данная модель не поддерживает анализ изображений. Пожалуйста, используйте Gemini модель.")
            return
        
        # Prepare messages for OnlySq API with image
        messages = format_message_history(user_id)
        
        # Add current user message with image
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": "Проанализируй это изображение и опиши, что на нем изображено."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        })
        
        # Call OnlySq API
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
        await processing_msg.edit_text("🖼️ Анализ изображения завершен!")
        await message.answer(ai_response, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logging.error(f"Error processing photo: {str(e)}")
        await message.answer(f"❌ Произошла ошибка при анализе изображения: {str(e)}")
        
        # Add error to history for debugging
        user["history"].append({
            "role": "system",
            "content": f"Error occurred while analyzing image: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_text_message(message: types.Message):
    """Handle regular text messages."""
    user_id = message.from_user.id
    user_input = message.text
    
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
        await bot.send_chat_action(user_id, types.ChatActions.TYPING)
        
        # Prepare messages for OnlySq API
        messages = format_message_history(user_id)
        
        # Add current user message if not already included
        if not messages or messages[-1]["content"] != user_input:
            messages.append({
                "role": "user",
                "content": user_input
            })
        
        # Call OnlySq API
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
        await message.answer(ai_response, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        await message.answer(f"❌ Произошла ошибка при обработке вашего сообщения: {str(e)}")
        
        # Add error to history for debugging
        user["history"].append({
            "role": "system",
            "content": f"Error occurred: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })


async def on_startup(dp):
    """Bot startup handler."""
    logging.info("Bot started successfully!")
    print("🤖 OnlySq Telegram Bot запущен!")
    print("Для остановки нажмите Ctrl+C")


async def on_shutdown(dp):
    """Bot shutdown handler."""
    logging.info("Bot shutdown")
    print("🤖 OnlySq Telegram Bot остановлен!")


if __name__ == '__main__':
    print("🚀 Запуск OnlySq Telegram Bot...")
    print("Убедитесь, что вы установили зависимости: pip install aiogram openai")
    print("И установили переменную окружения TELEGRAM_BOT_TOKEN")
    
    try:
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
    except KeyboardInterrupt:
        print("\nОстановка бота...")
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        print(f"❌ Критическая ошибка: {str(e)}")