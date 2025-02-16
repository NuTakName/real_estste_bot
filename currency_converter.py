import requests
import ring

from loguru import logger

from core import CurrencyType

API_LINK = "https://api.exchangerate-api.com/v4/latest/RUB"


@ring.lru(maxsize=2040)
def get_amount_for_ads(user_currency: CurrencyType, amount: float):
    if user_currency == "RUB":
        return f"{round(amount)} RUB"
    try:
        response = requests.get(API_LINK, timeout=3)
        if response.status_code == 200:
            result = response.json()
            if user_currency == "USD":
                res = result["rates"]["USD"]
            else:
                res = result["rates"]["EUR"]
            value = res * amount
            return f"{round(value)} {user_currency.value}"
        else:
            return f"{amount} RUB"
    except Exception as e:
        logger.warning(e)
        return f"{amount} RUB"
