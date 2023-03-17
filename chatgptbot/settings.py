from logging import warning
from pydantic import BaseModel, Field, validator

MODELS = "text-davinci-003,text-curie-001,text-babbage-001,text-ada-001,gpt-3.5-turbo".split(',')
SIZES = '256x256','512x512','1024x1024'

class newSettings(BaseModel):
    max_token: int = Field(1000)
    bot_personality: str = Field("Answer in professional tone")
    model: str = Field(MODELS[4])
    imageSize: str = Field('1024x1024')
    show_choises: int = Field(1)

    @validator('max_token')
    def max_token_validate(cls, v):
        if v>2048 or v<10:
            raise ValueError('max_token must be betwin 10 and 2048')
        return v


    @validator("model")
    def model_validate(cls, v):
        if v not in MODELS:
            ValueError(f"Model must be one of this: {MODELS}")
        return v

    @validator('imageSize')
    def imageSizeValidate(cls,v:str):
        if v not in SIZES:
            ValueError(f'size must be one of {SIZES}')
        return v


class Settings:

    def __init__(self):
        self.max_token = 1000
        self.history_length = 10
        self.bot_personality = "Answer in professional tone"
        self.model = MODELS[4]
        self.show_completitions = 1
        self.imageSize = "1024x1024"


    def __setattr__(self, attr, value):
        match attr:
            case "max_token":
                value = int(value)
                if type(value)!=type(0) or value>2048 or value<10:
                    raise ValueError('max_token must be int in range from 10 to 2048')
            case "model":
                if value not in MODELS:
                    warning(repr(value))
                    warning(repr(MODELS[0]))
                    raise ValueError(f"Got {value} expected one of: {MODELS}")
            case "history_length":
                value = int(value)
                if type(value) != type(0) or value<0:
                    raise ValueError('history_length must be positive')
            case "bot_personality":
                if type(value) != type("str") or not value:
                    raise ValueError("bot_personality cant be blank")

        super().__setattr__(attr, value)

    def getDict(self):
        return self.__dict__

    @classmethod
    def fromDict(cls, settingsDict):
        result = cls()
        cls.__init__(result)
        result.__dict__ = settingsDict
        return result
                
DEFAULT = Settings()
warning('DEFAULTS')
warning(f"bot_personality: { DEFAULT.bot_personality }")
warning(f"model of engine: { DEFAULT.model }")
warning(f"max_token: { DEFAULT.max_token }")
