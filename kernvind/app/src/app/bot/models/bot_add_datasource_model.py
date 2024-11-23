from pydantic import BaseModel

class BotAddDataSource(BaseModel):
    bot_id: int
    datasource_id: int