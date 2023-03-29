from collectors import COLLECTORS
from confluent_kafka import Producer
from dotenv import load_dotenv
from models import *
from json import dumps
from os import getenv
from socket import gethostname
from asyncio import run as asyncio
from asyncio import gather
from typing import (Awaitable, Tuple, List)
from loguru import logger

load_dotenv()


class ProducerSession:

    def __init__(self, producer: Producer, topic: str, value: bytes):
        self.producer = producer
        self.topic = topic
        self.value = value

    def __enter__(self):
        self.producer.produce(topic=self.topic, value=self.value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.producer.flush()


class Storage():
    def __enter__(self):
        kafka_configuration = {'bootstrap.servers': f"{getenv('KAFKA_HOST')}:{getenv('KAFKA_PORT')}",
                               "client.id": gethostname()}
        self.collectors: List[Collector] = list(map(lambda factory_register: factory_register(), COLLECTORS))
        self.producer = Producer(kafka_configuration)
        self.logger = logger
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.producer.close()


class Enricher:

    @staticmethod
    async def enrich():
        with Storage() as deps:
            while True:
                try:
                    tasks: Tuple[ChannelName, Order] = list(
                        map(lambda coroutine: coroutine.fetch_order(), deps.collectors))

                    results = await gather(*tasks)

                    for result in results:
                        converted_orders: list[dict] = list(map(lambda order: order.dict(), result[1]))
                        formatted_orders: str = dumps(converted_orders)

                    with ProducerSession(producer=deps.producer, topic=result[0],
                                         value=formatted_orders.encode('utf-8')) as producer_session:
                        deps.logger.info(f"Enricher produced data to the channel {producer_session.topic}")

                except Exception as error:
                    deps.logger.error(error)


asyncio(Enricher.enrich())
