"""A tiny shop module with one planted bug, used by demo/mini_agent.py."""


def apply_discount(price: float, percent: float) -> float:
    """Return the price after a percentage discount. 10 means 10% off."""
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return price * percent / 100


def cart_total(prices: list[float], percent: float = 0) -> float:
    """Sum the prices, then apply the discount once to the total."""
    return round(apply_discount(sum(prices), percent), 2)
