from cached_data.sigleton import Singleton
from core.garage.models import Garage

class CachedGarage(metaclass=Singleton):
    cached_sale_garage: dict = {}
    cached_rent_garage: dict = {}

    async def loads_data_garages(self):
        sale_houses, rent_houses = await Garage.get_garages()
        self.cached_sale_garage = sale_houses
        self.cached_rent_garage = rent_houses

    async def get(self, action: str) -> Garage:
        if self.cached_sale_garage is None or self.cached_rent_garage is None:
            await self.loads_data_garages()
        garages = self.cached_sale_garage if action == "buy_garage" else self.cached_rent_garage
        return next(iter(garages.values()), None) if garages else None


    def get_next(self, action: str, index: int) -> Garage | None:
        garage = self.cached_sale_garage if action == "buy_garage" else self.cached_rent_garage
        garage_ids = list(garage.keys())
        next_index = (index + 1) % len(garage_ids)
        return garage[garage_ids[next_index]]

    def get_previous(self, action: str, index: int) -> Garage | None:
        garage = self.cached_sale_garage if action == "buy_garage" else self.cached_rent_garage
        garage_ids = list(garage.keys())
        previous_index = (index - 1) % len(garage_ids)
        return garage[garage_ids[previous_index]]