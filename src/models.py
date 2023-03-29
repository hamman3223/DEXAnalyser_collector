from pydantic import (BaseModel, AnyHttpUrl)
from abc import (ABC, abstractmethod)
from typing import (TypedDict, Union)


class CollectorConfig(BaseModel):
    base_url: str
    endpoint: str


class ChannelName(TypedDict):
    name: str
    category: str


class Order(ABC):
    orderHash: str
    makerAsset: str
    takerAsset: str
    exchangeRate: Union[float, str]


class Collector(ABC):

    @property
    @abstractmethod
    def collector_name(self):
        ...

    @property
    @abstractmethod
    def config(self):
        ...

    @config.setter
    def config(self, value):
        ...

    @abstractmethod
    def __init__(self, cfg: CollectorConfig) -> None:
        ...

    @staticmethod
    async def fetch_order(*args, **kwargs) -> Order:
        ...
