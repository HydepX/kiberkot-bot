# catalog.py

CATEGORIES = {
    "mice": "🖱 Мыши",
    "keyboards": "⌨️ Клавиатуры",
    "headsets": "🎧 Гарнитуры",
    "micepads": "🖲 Коврики",
    "microphones": "🎙 Микрофоны",
}

# 30 товаров. У каждого уникальный ID для кнопок и БД.
PRODUCTS = {
    # --- МЫШИ (6) ---
    "m_01": {"id": "m_01", "cat": "mice", "name": "Razer Viper V4 Pro", "price": 16990, "specs": "54г, Focus Pro 36K, оптические свитчи Gen-3, 110ч работы"},
    "m_02": {"id": "m_02", "cat": "mice", "name": "Razer DeathAdder V3 Pro", "price": 14990, "specs": "63г, Focus Pro 30K, эргономика, 90ч работы"},
    "m_03": {"id": "m_03", "cat": "mice", "name": "Razer Basilisk V3 Pro", "price": 15990, "specs": "114г, Focus Pro 30K, умный скролл, RGB"},
    "m_04": {"id": "m_04", "cat": "mice", "name": "Razer Naga V2 Pro", "price": 13990, "specs": "MMO мышь, 12 боковых кнопок, сменные панели"},
    "m_05": {"id": "m_05", "cat": "mice", "name": "Razer Orochi V2", "price": 6990, "specs": "Компактная, Bluetooth/2.4G, до 450ч работы"},
    "m_06": {"id": "m_06", "cat": "mice", "name": "Razer DeathAdder V3 Hyperspeed", "price": 8990, "specs": "55г, Focus Pro 30K, бюджетный киберспорт"},

    # --- КЛАВИАТУРЫ (6) ---
    "k_01": {"id": "k_01", "cat": "keyboards", "name": "Razer Huntsman V3 Pro", "price": 24990, "specs": "Аналоговые оптические свитчи, Rapid Trigger, регулировка актуации"},
    "k_02": {"id": "k_02", "cat": "keyboards", "name": "Razer BlackWidow V4 Pro", "price": 22990, "specs": "Зеленые свитчи, макро-клавиши, командный диск, подставка под запястья"},
    "k_03": {"id": "k_03", "cat": "keyboards", "name": "Razer BlackWidow V3 Pro", "price": 17990, "specs": "Зеленые/Желтые свитчи, беспроводная, RGB"},
    "k_04": {"id": "k_04", "cat": "keyboards", "name": "Razer Ornata V3 X", "price": 4990, "specs": "Мембранно-механическая, тихая, бюджетная"},
    "k_05": {"id": "k_05", "cat": "keyboards", "name": "Razer Huntsman Mini Analog", "price": 16990, "specs": "60% формат, аналоговые свитчи, двойное нажатие"},
    "k_06": {"id": "k_06", "cat": "keyboards", "name": "Razer BlackWidow V4 75%", "price": 19990, "specs": "75% формат, желтые линейные свитчи, алюминиевая рама"},

    # --- ГАРНИТУРЫ (6) ---
    "h_01": {"id": "h_01", "cat": "headsets", "name": "Razer BlackShark V2 Pro (2023)", "price": 18990, "specs": "50мм динамики, Focus+ Aiming, до 70ч работы, USB-C"},
    "h_02": {"id": "h_02", "cat": "headsets", "name": "Razer Kraken V3 Pro", "price": 15990, "specs": "50мм динамики, HyperSense (тактильная отдача), THX Spatial"},
    "h_03": {"id": "h_03", "cat": "headsets", "name": "Razer Barracuda X", "price": 9990, "specs": "Универсальная (PC/Mobile), 40мм динамики, 50ч работы, 275г"},
    "h_04": {"id": "h_04", "cat": "headsets", "name": "Razer Kraken Kitty V2", "price": 13990, "specs": "RGB-ушки, THX Spatial, мягкие амбушюры"},
    "h_05": {"id": "h_05", "cat": "headsets", "name": "Razer Nari Ultimate", "price": 11990, "specs": "Тактильная отдача, автобаланс звука/чата"},
    "h_06": {"id": "h_06", "cat": "headsets", "name": "Razer BlackShark V2 X", "price": 5990, "specs": "Проводная, 50мм динамики, 7.1 объемный звук, легкая"},

    # --- КОВРИКИ (6) ---
    "p_01": {"id": "p_01", "cat": "micepads", "name": "Razer Firefly V2 Pro", "price": 12990, "specs": "Микро-текстурная поверхность, RGB Chroma, магнитное подключение"},
    "p_02": {"id": "p_02", "cat": "micepads", "name": "Razer Strider Chroma", "price": 8990, "specs": "Гибридный коврик, RGB по контуру, водостойкий"},
    "p_03": {"id": "p_03", "cat": "micepads", "name": "Razer Goliathus Extended", "price": 3990, "specs": "Тканевый, 920x300мм, микро-текстура"},
    "p_04": {"id": "p_04", "cat": "micepads", "name": "Razer Goliathus Speed", "price": 2490, "specs": "Быстрый тканевый, для низкого сенса"},
    "p_05": {"id": "p_05", "cat": "micepads", "name": "Razer Firefly V2", "price": 6990, "specs": "Жесткий/Тканевый, RGB Chroma, без провода"},
    "p_06": {"id": "p_06", "cat": "micepads", "name": "Razer Strider", "price": 4990, "specs": "Гибридный, жесткая основа, мягкое покрытие"},

    # --- МИКРОФОНЫ (6) ---
    "c_01": {"id": "c_01", "cat": "microphones", "name": "Razer Seiren V3 Mini", "price": 8990, "specs": "Конденсаторный, 24-бит/96 кГц, tap-to-mute, компактный"},
    "c_02": {"id": "c_02", "cat": "microphones", "name": "Razer Seiren V2", "price": 11990, "specs": "Кардиоида, встроенный поп-фильтр, шоковое крепление"},
    "c_03": {"id": "c_03", "cat": "microphones", "name": "Razer Seiren V3 Chroma", "price": 14990, "specs": "RGB подсветка, 2 конденсаторных капсулы, сенсорный mute"},
    "c_04": {"id": "c_04", "cat": "microphones", "name": "Razer Seiren V3 Multi-Pattern", "price": 16990, "specs": "4 диаграммы направленности, для подкастов и стримов"},
    "c_05": {"id": "c_05", "cat": "microphones", "name": "Razer Seiren BT", "price": 7990, "specs": "Беспроводной Bluetooth, 24ч работы, компактный"},
    "c_06": {"id": "c_06", "cat": "microphones", "name": "Razer Seiren X", "price": 5990, "specs": "Базовый стримерский, суперкардиоида, нулевая задержка"},
}

# --- Поля-адаптеры, чтобы старые хендлеры работали без правок ---

_CAT_EMOJI = {
    "mice": "🖱",
    "keyboards": "⌨️",
    "headsets": "🎧",
    "micepads": "🖲",
    "microphones": "🎙",
}

for _pid, _p in PRODUCTS.items():
    _p["emoji"] = _CAT_EMOJI[_p["cat"]]
    _p["short"] = _p["specs"]

# Характеристики для Qwen (Блок 3)
SPECS = {pid: p["specs"] for pid, p in PRODUCTS.items()}


# --- Новые хелперы (Блок 4) ---

def get_product_by_id(product_id: str):
    return PRODUCTS.get(product_id)


def get_products_by_category(category: str):
    return [p for p in PRODUCTS.values() if p["cat"] == category]


def get_all_products_for_prompt() -> str:
    """Строка для промпта Qwen со всем каталогом."""
    lines = []
    for p in PRODUCTS.values():
        lines.append(f"[{p['id']}] {p['name']} ({p['price']} руб.) - {p['specs']}")
    return "\n".join(lines)


# --- Старая логика подбора сетапов (работает до Шага 2) ---

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

# Приоритеты пересопоставлены на новые ID флагманов
TASK_PRIORITY = {
    "mmo": ["k_01", "m_01", "h_01", "p_01", "c_01"],
    "aim": ["m_01", "p_01", "k_01", "h_01", "c_01"],
    "esports": ["m_01", "k_01", "p_01", "h_01", "c_01"],
    "stream": ["c_01", "h_01", "k_01", "m_01", "p_01"],
    "universal": ["m_01", "k_01", "h_01", "p_01", "c_01"],
}

BUDGET_ITEM_COUNT = {
    "b1": 1,
    "b2": 2,
    "b3": 4,
    "b4": 5,
}


def get_setup_products(task: str, budget: str) -> list:
    priority = TASK_PRIORITY.get(task, TASK_PRIORITY["universal"])
    limit = BUDGET_ITEM_COUNT.get(budget, 5)
    return priority[:limit]


def calculate_total(product_ids: list) -> int:
    return sum(PRODUCTS[product_id]["price"] for product_id in product_ids)


def format_price(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def format_setup_text(product_ids: list) -> str:
    lines = []
    for product_id in product_ids:
        product = PRODUCTS[product_id]
        lines.append(f"{product['emoji']} {product['name']} — {product['short']}")

    total = calculate_total(product_ids)
    lines.append("")
    lines.append(f"Ориентировочная стоимость: {format_price(total)} ₽")

    return "\n".join(lines)
