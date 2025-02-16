from cached_data.sigleton import Singleton
from core import Flat


class CachedFlat(metaclass=Singleton):
    cached_sale_flats: dict = {}
    cached_rent_flats: dict = {}

    async def loads_data_flats(self):
        sale_flats, rent_flats = await Flat.get_flats()
        self.cached_sale_flats = sale_flats
        self.cached_rent_flats = rent_flats

    async def get(self, action: str) -> Flat:
        if self.cached_sale_flats is None or self.cached_rent_flats is None:
            await self.loads_data_flats()
        flats = self.cached_sale_flats if action == "buy_flat" else self.cached_rent_flats
        return next(iter(flats.values()), None) if flats else None

    def get_next(self, action: str, index: int) -> Flat | None:
        flats = self.cached_sale_flats if action == "buy_flat" else self.cached_rent_flats
        flat_ids = list(flats.keys())
        next_index = (index + 1) % len(flat_ids)
        return flats[flat_ids[next_index]]

    def get_previous(self, action: str, index: int) -> Flat | None:
        flats = self.cached_sale_flats if action == "buy_flat" else self.cached_rent_flats
        flat_ids = list(flats.keys())
        previous_index = (index - 1) % len(flat_ids)
        return flats[flat_ids[previous_index]]

