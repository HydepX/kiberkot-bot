PRODUCTS = {
    "viper_v4_pro": {
        "emoji": "🖱",
        "name": "Viper V4 Pro",
        "category": "mouse",
        "price": 16990,
        "short": "лёгкая киберспортивная мышь",
    },
    "huntsman_v3_pro": {
        "emoji": "⌨️",
        "name": "Huntsman V3 Pro",
        "category": "keyboard",
        "price": 22990,
        "short": "быстрая клавиатура для игр",
    },
    "blackshark_v2_pro": {
        "emoji": "🎧",
        "name": "BlackShark V2 Pro",
        "category": "headset",
        "price": 18990,
        "short": "игровая гарнитура с позиционированием звука",
    },
    "firefly_v2_pro": {
        "emoji": "🔥",
        "name": "Firefly V2 Pro",
        "category": "mousepad",
        "price": 10990,
        "short": "ковёр с подсветкой и плотной поверхностью",
    },
    "seiren_v3_mini": {
        "emoji": "🎤",
        "name": "Seiren V3 Mini",
        "category": "microphone",
        "price": 11990,
        "short": "компактный микрофон для стримов и войса",
    },
}


GAMES = {
    "valorant": "Valorant",
    "cs2": "CS2",
    "dota2": "Dota 2",
    "fortnite": "Fortnite",
    "other": "Другая",
}


TASKS = {
    "mmo": "MMO/RPG: комфорт нажатий и макросы",
    "aim": "Максимальный аим и точность",
    "esports": "Быстрая реакция и киберспорт",
    "stream": "Стримы и голосовая связь",
    "universal": "Универсальный сетап",
}


BUDGETS = {
    "b1": "До 25 000 ₽",
    "b2": "25 000 — 50 000 ₽",
    "b3": "50 000 — 80 000 ₽",
    "b4": "80 000+ ₽",
}


TASK_PRIORITY = {
    "mmo": [
        "huntsman_v3_pro",
        "viper_v4_pro",
        "blackshark_v2_pro",
        "firefly_v2_pro",
        "seiren_v3_mini",
    ],
    "aim": [
        "viper_v4_pro",
        "firefly_v2_pro",
        "huntsman_v3_pro",
        "blackshark_v2_pro",
        "seiren_v3_mini",
    ],
    "esports": [
        "viper_v4_pro",
        "huntsman_v3_pro",
        "firefly_v2_pro",
        "blackshark_v2_pro",
        "seiren_v3_mini",
    ],
    "stream": [
        "seiren_v3_mini",
        "blackshark_v2_pro",
        "huntsman_v3_pro",
        "viper_v4_pro",
        "firefly_v2_pro",
    ],
    "universal": [
        "viper_v4_pro",
        "huntsman_v3_pro",
        "blackshark_v2_pro",
        "firefly_v2_pro",
        "seiren_v3_mini",
    ],
}


BUDGET_ITEM_COUNT = {
    "b1": 1,
    "b2": 2,
    "b3": 4,
    "b4": 5,
}


def get_setup_products(task: str, budget: str) -> list[str]:
    """
    Возвращает список товаров для сетапа
    в зависимости от задачи и бюджета.
    """
    priority = TASK_PRIORITY.get(task, TASK_PRIORITY["universal"])
    limit = BUDGET_ITEM_COUNT.get(budget, 5)
    return priority[:limit]


def calculate_total(product_ids: list[str]) -> int:
    """
    Считает суммарную стоимость сетапа.
    """
    return sum(PRODUCTS[product_id]["price"] for product_id in product_ids)


def format_price(value: int) -> str:
    """
    Форматирует цену: 69960 -> 69 960
    """
    return f"{value:,}".replace(",", " ")


def format_setup_text(product_ids: list[str]) -> str:
    """
    Формирует текст сетапа.
    """
    lines = []

    for product_id in product_ids:
        product = PRODUCTS[product_id]
        lines.append(
            f"{product['emoji']} {product['name']} — {product['short']}"
        )

    total = calculate_total(product_ids)
    lines.append("")
    lines.append(f"Ориентировочная стоимость: {format_price(total)} ₽")

    return "\n".join(lines)
