class SubscriptionInfo:
    def __init__(self, asset: str, min_threshold: float, max_threshold: float):
        self.asset = asset
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
