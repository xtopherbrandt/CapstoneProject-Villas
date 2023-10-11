import enum

class ExtendedEnum(enum.Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
    
class Country(ExtendedEnum):
    CAN = 'Canada'
    USA = 'United States of America'
