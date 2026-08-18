import json
import logging

import aiohttp

from config import DASHSCOPE_API_KEY
from catalog import PRODUCTS, SPECS

logger = logging.getLogger(__name__)

# ---------- Промпт-классификатор интентов ----------

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

# ---------- Промпт для ответов на вопросы ----------

QA_SYSTEM_PROMPT = """
Ты — КиберКот 🟢, дружелюбный эксперт-геймер и консультант магазина периферии Razer.
Отвечай на вопрос пользователя КОРОТКО: 2–4 предложения, простым языком, с лёгким геймерским вайбом.
Используй ТОЛЬКО базу знаний ниже. Не выдумывай характеристики.
Если в базе нет ответа — честно скажи: "Точных данных у меня нет 🙈" и предложи нажать кнопку «❓ Вопрос по товару», чтобы менеджер ответил лично.

База знаний:
{knowledge}
"""

ENDPOINTS = (
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
)

# ---------- Локальный fallback ----------

RETURN_WORDS = (
    "верн", "возврат", "брак", "сломал", "не работает",
    "обмен", "дефект", "отдать обратно",
)
QUESTION_WORDS = (
    "какой", "какая", "какие", "вес", "rgb", "подойдет",
    "совмест", "характеристик", "есть ли", "поддерж",
    "весит", "для кс", "для дот", "для валор",
    "устроена", "работает", "расскажи", "обзор", "отлич",
    "почему", "что лучше", "как выбрать",
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


def build_knowledge() -> str:
    lines = []
    for product_id, product in PRODUCTS.items():
        specs = SPECS.get(product_id, product["short"])
        lines.append(
            f"- {product['emoji']} {product['name']}: {specs}. Цена: {product['price']} ₽."
        )
    return "\n".join(lines)


# ---------- Общий запрос к Qwen ----------

async def _post_qwen(messages: list, max_tokens: int):
    """
    Отправляет запрос в Qwen (пробует оба endpoint'а).
    Возвращает текст ответа или None.
    """
    if not DASHSCOPE_API_KEY:
        logger.warning("DASHSCOPE_API_KEY not set")
        return None

    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "qwen-plus",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }

    for url in ENDPOINTS:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    body = await resp.text()

                    if resp.status != 200:
                        logger.error(f"Qwen API error {resp.status} on {url}: {body[:300]}")
                        continue

                    data = json.loads(body)
                    return (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip()
                    )
        except Exception as e:
            logger.error(f"Qwen call failed ({url}): {e}")
            continue

    return None


# ---------- Классификация ----------

async def classify_qwen(text: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]
    content = await _post_qwen(messages, max_tokens=10)
    if not content:
        return None

    first = content.split()[0].strip(".,;:!?\"'").lower()
    if first in ("buy", "return", "question", "other"):
        return first

    logger.warning(f"Qwen unexpected answer: {content!r}")
    return None


async def classify_intent(text: str) -> str:
    if not text or len(text.strip()) < 2:
        return "other"

    intent = await classify_qwen(text)
    if intent is not None:
        logger.info(f"Qwen resolved: '{text}' -> {intent}")
        return intent

    intent = classify_local(text)
    logger.info(f"Local fallback: '{text}' -> {intent}")
    return intent


# ---------- Ответы на вопросы ----------

async def answer_question(text: str):
    """
    Отвечает на вопрос о товарах через Qwen с базой знаний.
    Возвращает текст ответа или None, если API недоступен.
    """
    messages = [
        {"role": "system", "content": QA_SYSTEM_PROMPT.format(knowledge=build_knowledge())},
        {"role": "user", "content": text},
    ]
    return await _post_qwen(messages, max_tokens=200)
