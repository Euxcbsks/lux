from enum import Enum, StrEnum, auto


class Modes(StrEnum):
    DEV = auto()
    DEVELOP = auto()
    DEVELOPMENT = auto()
    PROD = auto()
    PRODUCT = auto()
    PRODUCTION = auto()

    def is_dev(self):
        return self in [self.DEV, self.DEVELOP, self.DEVELOPMENT]

    def is_prod(self):
        return self in [self.PROD, self.PRODUCT, self.PRODUCTION]

    @property
    def fullname(self):
        return self.DEVELOPMENT if self.is_dev() else self.PRODUCTION
