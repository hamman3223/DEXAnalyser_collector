import os
from models import *

from aiohttp import ClientSession
from urllib.parse import (urlparse)
from typing import (Union, List, Optional, Awaitable, Tuple)


class LinchOrder(BaseModel, Order):
    orderHash: str
    makerAsset: str
    takerAsset: str
    makingAmount: int
    takingAmount: int
    exchangeRate: Union[float, str]
    #
    # def __init__(self, struct: dict):
    #     self.orderHash = struct.get('orderHash')
    #     self.makerAsset = struct['data'].get('makerAsset')
    #     self.takerAsset = struct['data'].get('takerAsset')
    #     self.makingAmount = int(struct['data'].get('makingAmount'))
    #     self.takingAmount = int(struct['data'].get('takingAmount'))
    #     self.exchangeRate = float(self.makingAmount / self.takingAmount)


class LinchConfig(CollectorConfig):
    takerAsset: Optional[str]
    makerAsset: Optional[str]
    limit: int = 500
    page: int = 1
    statuses: List[str] = ['1']


class LinchCollector(Collector):

    def __init__(self, cfg: LinchConfig) -> None:
        self._collector_name = "linch-collector"
        self._config = cfg

    @property
    def collector_name(self):
        return self._collector_name

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value
        if self._config.endpoint.startswith("/"): self._config.endpoint = self._config.endpoint[1::]

    async def fetch_order(self) -> Tuple[ChannelName, List[LinchOrder]]:

        if self._config.statuses:
            statuses = list(map(lambda status: str(status), self._config.statuses))

        params = {}
        if self._config.takerAsset:
            params.update({"takerAsset": self._config.takerAsset})

        if self._config.makerAsset:
            params.update({"makerAsset": self._config.makerAsset})

        if self._config.limit:
            params.update({"limit": self._config.limit})

        if self._config.page:
            params.update({"page": self._config.page})

        if self._config.statuses:
            params.update({"statuses": f'[{", ".join(self._config.statuses)}]'})

        _ = urlparse(self._config.base_url)

        url = f'{_.scheme}://{_.netloc}{_.path}{self._config.endpoint}'
        del _
        async with ClientSession() as session:
            res = await session.request(
                method="GET",
                url=url,
                params=params,
                verify_ssl=False
            )

            result = await res.json()
            result: List[LinchOrder] = list(map(lambda order:
                                                LinchOrder(orderHash=order.get('orderHash'),
                                                           makerAsset=order['data'].get('makerAsset'),
                                                           takerAsset=order['data'].get('takerAsset'),
                                                           makingAmount=int(order['data'].get('makingAmount')),
                                                           takingAmount=int(order['data'].get('takingAmount')),
                                                           exchangeRate=float(
                                                               int(order['data'].get('makingAmount')) / int(
                                                                   order['data'].get(
                                                                       'takingAmount')))),
                                                result))
            return (self.collector_name, result)


class LinchCollectorFactory:

    @staticmethod
    def register():
        return LinchCollector(
            cfg=LinchConfig(base_url=os.environ.get('LINCH_URL'),
                            endpoint=f"v3.0/{os.environ['NETWORK_ID']}/limit-order/all"))
