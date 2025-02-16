import asyncio

from playwright.async_api import async_playwright, TimeoutError, BrowserContext
from loguru import logger
from parser.base_parser import BaseParser


class VdndParser(BaseParser):

    URL = "https://vndn.club/"
    HEADLESS = False
    WORKERS = 3
    OPEN_ESTATE_TIMEOUT = 60000

    async def search_for_estates(self) -> None:
        estate_list = []
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.HEADLESS)
            context = await browser.new_context()
            await context.clear_cookies()
            page = await context.new_page()
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    " AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/88.0.4324.104 Safari/537.36"
                )
            }
            await page.set_extra_http_headers(headers)
            await page.goto(self.URL, timeout=60000)
            await page.wait_for_load_state("domcontentloaded")
            while True:

                try:
                    estates = await page.locator("li.item-object > a:nth-child(1)").all()
                    for estate in estates:
                        estate_link = await estate.get_attribute("href")
                        e = {
                            "link": f"https://vndn.club{estate_link}"
                        }
                        estate_list.append(e)
                        self.save_data_to_json("parser/vdnd/estate.json", estate_list)
                    next_page = page.locator(".object-pagination").get_by_text(">")
                    if next_page and await next_page.is_visible():
                        await next_page.click()
                        await page.wait_for_load_state("domcontentloaded")
                    else:
                        break
                except TimeoutError:
                    break


    async def parse_estate(self, estate: dict, context: BrowserContext) -> dict:
        photo_links = []
        city = None
        district = None
        type_ = None
        floor = None
        the_general_area = None
        rooms = None
        address = None
        estate_link = estate.get("link")
        await context.clear_cookies()
        page = await context.new_page()
        try:
            await page.goto(estate_link, timeout=self.OPEN_ESTATE_TIMEOUT)
            await page.wait_for_load_state()
            try:
                photos = await page.locator(".galleria").get_by_role("img").all()
                if len(photos) >= 2:
                    for photo in photos:
                        if len(photo_links) >= 3:
                            break
                        try:
                            photo_link = await photo.get_attribute("src")
                            photo_src = f"https://vndn.club{photo_link}"
                            if photo_src not in photo_links:
                                photo_links.append(photo_src)
                        except TimeoutError:
                            logger.warning("No founded photo src")
                            break
            except TimeoutError:
                logger.warning("No photos")
                await page.close()
            try:
                description = await page.locator(".object-description > p:nth-child(3)").inner_text()
            except TimeoutError:
                description = None
            try:
                phone = await page.locator(
                    ".object-card > ul:nth-child(1) > li:nth-child(3) > b:nth-child(1)"
                ).inner_text()
            except TimeoutError:
                phone = None
            try:
                price = await page.locator(".object-card > ul:nth-child(1) > li:nth-child(1)").inner_text()
            except TimeoutError:
                price = 0
            try:
                titles = await page.locator(".estate-info > tbody:nth-child(1) > tr > td:nth-child(1)").all()
                values = await page.locator(".estate-info > tbody:nth-child(1) > tr > td:nth-child(2)").all()
                for title, value in zip(titles, values):
                    t = await title.inner_text()
                    v = await value.inner_text()
                    if t == "Город:":
                        city = v
                    elif t == "Район:":
                        district = v
                    elif t == "Вид:":
                        type_ = v
                    elif t == "Этажность:":
                        floor = v
                    elif t == "Площадь:":
                        the_general_area = v
                    elif t == "Кол-во комнат:":
                        rooms = v
                    elif t == "Улица:":
                        address = v
            except TimeoutError:
                await page.close()
            estate_data = {
                "city": city,
                "district": district,
                "address": address,
                "type_": type_,
                "floor": floor,
                "the_general_area": the_general_area,
                "rooms": rooms,
                "description": description,
                "phone": phone,
                "price": price,
                "photos": photo_links
            }
            estate_data.update(estate)
            await page.close()
            return estate_data
        except TimeoutError as e:
            await page.close()
            logger.critical(e)
            logger.critical(estate_link)





    async def run(self):
        payload = self.load_data_from_json(fname="parser/vdnd/estate.json")
        if not payload:
            await self.search_for_estates()
            payload = self.load_data_from_json(fname="parser/vdnd/estate.json")
        not_parsed_estate = [data for data in payload if data.get("description") is None]
        await self.parse_all_estate(not_parsed_estate)
        await self.save_all_estates()
        return True



if __name__ == "__main__":
    parser = VdndParser()
    asyncio.run(parser.run())