from enum import StrEnum, auto
from typing import Literal


class Modes(StrEnum):
    DEV = auto()
    DEVELOP = auto()
    DEVELOPMENT = auto()
    PROD = auto()
    PRODUCT = auto()
    PRODUCTION = auto()

    def is_dev(self) -> bool:
        return self in [self.DEV, self.DEVELOP, self.DEVELOPMENT]

    def is_prod(self) -> bool:
        return self in [self.PROD, self.PRODUCT, self.PRODUCTION]

    @property
    def fullname(self) -> Literal["DEVELOPMENT", "PRODUCTION"]:
        return self.DEVELOPMENT.name if self.is_dev() else self.PRODUCTION.name
