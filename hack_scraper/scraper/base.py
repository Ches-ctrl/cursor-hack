from abc import ABC, abstractmethod
import pandas as pd

class BaseScraper(ABC):
    def __init__(self, proxy: str | None = None):
        self.proxy = proxy

    @abstractmethod
    async def scrape(self, limit: int) -> pd.DataFrame:
        """Scrape events and return as DataFrame"""
        pass
