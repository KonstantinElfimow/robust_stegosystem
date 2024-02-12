import datetime
from typing import Optional
from pydantic import BaseModel


class UserValidator(BaseModel):
    image: str
    registered_at: Optional[datetime.datetime]
