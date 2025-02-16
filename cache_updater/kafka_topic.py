from enum import Enum


class KafkaTopics(str, Enum):
    RELOAD_FLATS = "reload_flats"
    RELOAD_HOUSES = "reload_houses"
    RELOAD_GARAGES = "reload_garage"
    RELOAD_ADS = "reload_ads"
    RELOAD_UNCONFIRMED_ADS = "reload_unconfirmed_ads"



