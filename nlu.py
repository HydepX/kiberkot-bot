import aiohttp
import logging
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Системный промпт с нашим "датасетом" (Few-Shot Prompting)
SYSTEM_PROMPT = """
Ты — строгий классификатор интентов для Telegram-бота магазина игровой периферии Razer.
Твоя задача: определить намерение пользователя по его сообщению.

Возможные интенты (возвращай ТОЛЬКО одно из этих слов):
- buy: Пользователь хочет купить товар, узнать цену, оформить заказ, собрать сетап. (Примеры: "хочу вайпер", "сколько стоит", "оформи заказ", "дай коврик").
- return: Пользователь хочет вернуть товар, жалуется на брак, просит обмен. (Примеры: "вернуть деньги", "свитчи бракованные", "оформить возврат").
- question: Пользователь спрашивает про характеристики, совместимость, наличие. (Примеры: "какой вес", "есть ли rgb", "подойдет для кс2").
- other: Приветствия, флуд, мусор, благодарность, или текст, который не подходит ни под одну категорию. (Примеры: "привет", "спс", "как дела").

Сообщение пользователя: "{user_text}"

Ответь ТОЛЬКО одним словом (buy, return, question или other) без лишних символов и объяснений.
"""

async def classify_intent(text: str) -> str:
    """
    Отправляет текст в Gemini 1.5 Flash и возвращает распознанный интент.
    """
    if not text or len(text.strip()) < 2:
        return "other"

    prompt = SYSTEM_PROMPT.format(user_text=text)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1, # Минимальная креативность, нам нужна точность
            "maxOutputTokens": 10
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Достаем текст ответа из структуры JSON Gemini
                    intent = data['candidates'][0]['content']['parts'][0]['text'].strip().lower()
                    
                    # Защита от галлюцинаций (если нейросеть вдруг ответит чем-то странным)
                    if intent in ["buy", "return", "question", "other"]:
                        return intent
                    else:
                        logger.warning(f"Gemini returned unexpected intent: {intent}")
                        return "other"
                else:
                    logger.error(f"Gemini API error: {resp.status} - {await resp.text()}")
                    return "other" # В случае ошибки API не ломаем бота, считаем это 'other'
                    
    except Exception as e:
        logger.error(f"Exception in NLU: {e}")
        return "other"
