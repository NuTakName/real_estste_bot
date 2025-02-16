from json import loads, dumps

from sqlalchemy.orm import declarative_base, QueryableAttribute

from cache_updater.kafka_sender import CacheUpdateProducer
from core.async_session import async_session

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True



    async def add(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
            kafka_produces = CacheUpdateProducer()
            await kafka_produces.update_cache_unconfirmed_ads()
            await kafka_produces.update_cache_my_ads()
        return self


    async def delete(self, type_: str):
        async with async_session() as session:
            await session.delete(self)
            await session.commit()
            kafka_produces = CacheUpdateProducer()
            await kafka_produces.update_cache(type_=type_, current_id=self.id)
            await kafka_produces.update_cache_my_ads()
            await kafka_produces.update_cache_unconfirmed_ads()


    def to_dict(self, _hide=None, _path=None):
        _hide = _hide or []
        hidden = self.__hidden_fields if hasattr(self, "__hidden_fields") else []

        if not _path:
            _path = self.__tablename__.lower()

            def prepend_path(item):
                item = item.lower()
                if item.split(".", 1)[0] == _path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != ".":
                    item = ".%s" % item
                item = "%s%s" % (_path, item)
                return item

            _hide[:] = [prepend_path(x) for x in _hide]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        ret_data = {}

        for key in columns:
            if key.startswith("_"):
                continue
            check = "%s.%s" % (_path, key)
            if check in _hide or key in hidden:
                continue
            ret_data[key] = getattr(self, key)

        for key in relationships:
            if key.startswith("_"):
                continue
            check = "%s.%s" % (_path, key)
            if check in _hide or key in hidden:
                continue
            _hide.append(check)
            is_list = self.__mapper__.relationships[key].uselist
            if is_list:
                items = getattr(self, key)
                if self.__mapper__.relationships[key].query_class is not None:
                    if hasattr(items, "all"):
                        items = items.all()
                ret_data[key] = []
                for item in items:
                    ret_data[key].append(
                        item.to_dict(
                            _hide=list(_hide),
                            _path=("%s.%s" % (_path, key.lower())),
                        )
                    )
            else:
                if (
                    self.__mapper__.relationships[key].query_class is not None
                    or self.__mapper__.relationships[key].instrument_class is not None
                ):
                    item = getattr(self, key)
                    if item is not None:
                        ret_data[key] = item.to_dict(
                            _hide=list(_hide),
                            _path=("%s.%s" % (_path, key.lower())),
                        )
                    else:
                        ret_data[key] = None
                else:
                    ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith("_"):
                continue
            if not hasattr(self.__class__, key):
                continue
            attr = getattr(self.__class__, key)
            if not (isinstance(attr, property) or isinstance(attr, QueryableAttribute)):
                continue
            check = "%s.%s" % (_path, key)
            if check in _hide or key in hidden:
                continue
            val = getattr(self, key)
            if hasattr(val, "to_dict"):
                ret_data[key] = val.to_dict(
                    hide=list(_hide),
                    _path=("%s.%s" % (_path, key.lower())),
                )
            else:
                try:
                    ret_data[key] = loads(dumps(val))
                except:
                    pass

        return ret_data