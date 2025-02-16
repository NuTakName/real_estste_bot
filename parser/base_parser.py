import asyncio
import json
import os

import aiofiles
import aiohttp

from json import JSONDecodeError

from notifiers.logging import NotificationHandler
from loguru import logger
from playwright.async_api import BrowserContext, async_playwright
from tqdm import tqdm

from config import settings
from core import Admin, Flat, House


class BaseParser:
    DEFAULT_TIMEOUT: int = 1000
    OPEN_ESTATE_TIMEOUT: int = 1000
    URL: str
    HEADLESS: bool
    WORKERS: int


    @staticmethod
    def setup_logging():
        param = {
            "token": settings[""],
            "chat_id": settings[""],
        }
        handler = NotificationHandler("telegram", defaults=param)
        logger.add(handler, level="ERROR", backtrace=True)


    @staticmethod
    def load_data_from_json(fname: str, repeat_call: bool | None = None) -> list:
        try:
            with open(fname, "r") as f:
                try:
                    data = json.load(f)
                    return data
                except JSONDecodeError as e:
                    logger.critical(e)
        except FileNotFoundError:
            if repeat_call:
                return []
            else:
                logger.warning(f"File {fname} not found, creating...")
                return []


    @staticmethod
    def save_data_to_json(fname: str, data: list):
        with open(fname, "w+") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)



    @staticmethod
    async def download_image(link: str) -> str | None:
        if "no_photo" in link:
            return None
        fpath = f"photos/{link.split('/')[-1]}"
        if os.path.isfile(fpath):
            return link.split('/')[-1]
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(link, timeout=10) as response:
                    if response.status == 200:
                        fpath = f"photos/{link.split('/')[-1]}"
                        data = await response.read()
                        async with aiofiles.open(fpath, "wb") as f:
                            await f.write(data)
                        return fpath
            except Exception as e:
                logger.error(e)


    @staticmethod
    def parse_the_general_area(estate: dict) -> int:
        value = 0
        the_general_area = estate.get("the_general_area")
        results = the_general_area.split("/")
        for r in results:
            value += float(r)
        return value


    async def search_for_estates(self) -> None:
        raise NotImplementedError


    async def parse_estate(
            self, estate: dict,
            context: BrowserContext
    ) -> dict:
        raise NotImplementedError


    async def create_coroutine_parse_estate(
            self,
            semaphore: asyncio.Semaphore,
            estate: dict,
            context: BrowserContext
    ) -> dict:
        async with semaphore:
            estate = await self.parse_estate(estate, context)
        return estate


    async def parse_all_estate(self, estates_list: list):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            context = await browser.new_context()
            context.set_default_timeout(timeout=5000)
            semaphore = asyncio.Semaphore(self.WORKERS)
            coroutines = [
                self.create_coroutine_parse_estate(semaphore, estate_data, context)
                for estate_data in estates_list
            ]
            estates = asyncio.as_completed(coroutines)
            for estate in tqdm(estates, total=len(estates_list)):
                try:
                    e = await estate
                    estate_list = self.load_data_from_json("parser/vdnd/estate.json")
                    for item in estate_list:
                        if e:
                            if item.get("link") == e.get("link"):
                                item.update(e)
                    self.save_data_to_json("parser/vdnd/estate.json", estate_list)
                except Exception as e:
                    logger.warning(e)


    async def create_coroutine_insert_estate_into_db(self, semaphore: asyncio.Semaphore, estate: dict):
        async with semaphore:
            result = await self.insert_estates_into_db(estate)
            return result


    async def insert_estates_into_db(self, estate: dict):
        if len(estate) > 4:
            admin_user_id = await Admin.get_admin_user_id()

            type_ = estate.get("type_")
            the_general_area = self.parse_the_general_area(estate=estate)
            photos = []
            for photo_link in estate.get("photos"):
                photo = await self.download_image(photo_link)
                if photo:
                    photos.append(photo)
            if type_ == "Квартира":
                floor = estate.get("floor")
                split_floor = floor.split("/")
                flat = Flat(
                    city=estate.get("city"),
                    district=estate.get("district"),
                    rooms=int(estate.get("rooms")),
                    the_general_area=the_general_area,
                    floor=int(split_floor[0]),
                    info=estate.get("description"),
                    price=float(estate.get("price")),
                    photos=photos,
                    sale=True,
                    rent=False,
                    verification=False,
                    address=estate.get("address"),
                    phone=estate.get("mobile_phone"),
                    user_id=admin_user_id
                )
                return flat
            else:
                house = House(
                    city=estate.get("city"),
                    district=estate.get("district"),
                    rooms=int(estate.get("rooms")),
                    the_general_area=the_general_area,
                    info=estate.get("description"),
                    price=float(estate.get("price")),
                    photos=photos,
                    sale=True,
                    rent=False,
                    verification=False,
                    address=estate.get("address"),
                    phone=estate.get("mobile_phone"),
                    user_id=admin_user_id
                )
                return house


    async def save_all_estates(self):
        flats = []
        houses = []
        estates_list = self.load_data_from_json(fname="parser/vdnd/estate.json")
        semaphore = asyncio.Semaphore(self.WORKERS)
        coroutines = [
            self.create_coroutine_insert_estate_into_db(semaphore, estate_data)
            for estate_data in estates_list
        ]
        estates = asyncio.as_completed(coroutines)
        for estate in tqdm(estates, total=len(estates_list)):
            try:
                result = await estate
                if isinstance(result, Flat) and result.photos:
                    flats.append(result)
                elif isinstance(result, House) and result.photos:
                    houses.append(result)
            except Exception as e:
                logger.critical(e)
        await Flat.add_all(flats)
        await House.add_all(houses)