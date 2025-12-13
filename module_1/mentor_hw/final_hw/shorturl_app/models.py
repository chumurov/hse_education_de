from pydantic import BaseModel, HttpUrl, ConfigDict

class URLBase(BaseModel):
    url: HttpUrl

class URLCreate(URLBase):
    pass

class URLItem(URLBase):
    id: str
    model_config = ConfigDict(from_attributes=True)
