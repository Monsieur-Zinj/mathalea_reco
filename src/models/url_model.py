from pydantic import BaseModel, Field
from typing import Optional, Union, List

class UrlParamsModel(BaseModel):
    uuid: str
    id: str
    n: Optional[int] = 1
    d: Optional[int] = None
    s: Optional[Union[str, int, bool]] = None
    s2: Optional[Union[str, int, bool]] = None
    s3: Optional[Union[str, List[str]]] = None
    s4: Optional[Union[str, bool]] = None
    alea: str
    i: Optional[int] = None
    cd: Optional[int] = None
    title: Optional[str] = None
    es: Optional[str] = None

    class Config:
        extra = "allow"

        schema_extra = {
            "example": {
                "uuid": "db2e0",
                "id": "3L11",
                "n": 4,
                "d": 10,
                "s": "1",
                "s2": "2",
                "s3": "1-2-3-4",
                "s4": "false",
                "alea": "AlwE",
                "i": 1,
                "cd": 1
            }
        }
