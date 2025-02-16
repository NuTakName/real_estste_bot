from cached_data.sigleton import Singleton
from core import Garage


class UnconfirmedAds(metaclass=Singleton):
    data: list = []

    async def loads_data(self):
        data = await Garage.get_unconfirmed_ads()
        self.data = data


    async def get_data(self):
        if self.data is None:
            await self.loads_data()
        return next(iter(self.data), None) if self.data else None


    def remove_ads(self):
        self.data.pop(0)


