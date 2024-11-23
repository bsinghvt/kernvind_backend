from tortoise.models import Model
from tortoise import fields


class DataFeedSource(Model):
    """DataFeedSource model class 
    
    Fields are required unless specified can be null
    Inherits Model from tortoise.models

    Attributes:
        datafeedsource_id: string for name. max length 64
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    datafeedsource_id = fields.CharField(max_length=64, primary_key=True)
    created = fields.DatetimeField(auto_now_add= True)
    modified = fields.DatetimeField(auto_now= True)