# expected clean inventory columns used by the app
REQUIRED_COLUMNS = [
    "item_name",
    "current_stock",
    "min_stock",
    "daily_demand",
    "lead_days",
    "supplier",
    "category",
]

NUMERIC_COLUMNS = [
    "current_stock",
    "min_stock",
    "daily_demand",
    "lead_days",
]