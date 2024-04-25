class SubscriptionInfo:
    def __init__(self, symbol: str, min_threshold: float, max_threshold: float):
        self.symbol = symbol
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
