import logging

import aiohttp

from config import DASHSCOPE_API_KEY

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Ты — строгий классификатор интентов для Telegram-бота магазина игровой периферии Razer.
Определи намерение пользователя по его сообщению.

Возможные интенты (верни ТОЛЬКО одно слово):
- buy: хочет купить, узнать цену, оформить заказ, собрать сетап. Примеры: "хочу вайпер", "сколько стоит", "оформи заказ".
- return: хочет вернуть, жалуется на брак, просит обмен. Примеры: "вернуть деньги", "свитчи бракованные".
- question: вопрос о характеристиках, совместимости, наличии. Примеры: "какой вес", "есть ли rgb", "подойдет для кс2".
- other: приветствие, флуд, благодарность, непонятный текст. Примеры: "привет", "спс", "как дела".

Ответь одним словом без лишних символов.
"""

# ---------- Локальный fallback ----------

RETURN_WORDS = (
    "верн", "возврат", "брак", "сломал", "не работает",
    "обмен", "дефект", "отдать обратно",
)
QUESTION_WORDS = (
    "какой", "какая", "какие", "вес", "rgb", "подойдет",
    "совмест", "характеристик", "есть ли", "поддерж",
    "весит", "для кс", "для дот", "для валор",
)
BUY_WORDS = (
    "куп", "заказ", "цена", "стоит", "сетап", "собери",
    "подбери", "хочу", "дай", "нужен", "нужна", "нужно", "оформи",
)


def classify_local(text: str) -> str:
    t = text.lower()
    if any(w in t for w in RETURN_WORDS):
        return "return"
    if any(w in t for w in QUESTION_WORDS):
        return "question"
    if any(w in t for w in BUY_WORDS):
        return "buy"
    return "other"


# ---------- Qwen через DashScope (OpenAI-compatible) ----------

async def classify_qwen(text: str) -> str:
    """
    Пробует распознать через Qwen.
    Возвращает интент или None, если API недоступен.
    """
    if not DASHSCOPE_API_KEY:
        logger.warning("DASHSCOPE_API_KEY not set")
        return None

    url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "temperature": 0.1,
        "max_tokens": 10,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.error(f"Qwen API error: {resp.status} - {body}")
                    return None

                data = await resp.json()
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                    .lower()
                )

                # Вытаскиваем первое слово — на случай если модель болтливая
                first_word = content.split()[0] if content else ""
                # Убираем возможные точки/запятые
                first_word = first_word.strip(".,;:!?\n\t ")

                if first_word in ("buy", "return", "question", "other"):
                    return first_word

                logger.warning(f"Qwen returned unexpected: {content!r}")
                return None

    except Exception as e:
        logger.error(f"Exception in Qwen call: {e}")
        return None


# ---------- Основной вход ----------

async def classify_intent(text: str) -> str:
    """
    Пытается Qwen, при неудаче — локальный классификатор.
    """
    if not text or len(text.strip()) < 2:
        return "other"

    intent = await classify_qwen(text)
    if intent is not None:
        logger.info(f"Qwen resolved: '{text}' -> {intent}")
        return intent

    intent = classify_local(text)
    logger.info(f"Local fallback: '{text}' -> {intent}")
    return intent
