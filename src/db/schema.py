from pydantic import BaseModel


class UserValidator(BaseModel):
    image_url: str
    complexity: float
    average_hash: int
    phash: int
    dhash: int
    hash_size: int
