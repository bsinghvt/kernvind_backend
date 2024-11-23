from tortoise.models import Model
from tortoise import fields


class Llm(Model):
    """Llm model class for database table 'llm'
    
    Inherits Model from tortoise.models
    Fields are required unless specified can be null
    Attributes:
        llm_name: string for llm name, also a primary key. max length 50
        llmmodeltype: ForeignKey to LlmModelType table. Field in table is llmmodeltype_id
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    llm_name = fields.CharField(max_length=50, primary_key=True)
    llmmodeltype = fields.ForeignKeyField('models.LlmModelType', related_name='llm_model_type', on_update=fields.NO_ACTION, on_delete=fields.NO_ACTION)
    created = fields.DatetimeField(auto_now_add= True)
    modified = fields.DatetimeField(auto_now= True)
    class Meta: # type: ignore
        unique_together=(('llm_name','llmmodeltype'))

class LlmModelType(Model):
    """LlmModelType model class 
    
    Inherits Model from tortoise.models
    Fields are required unless specified can be null
    Attributes:
        llmmodeltype: string for llm name also a primary key. max length 50
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    llmmodeltype_name = fields.CharField(max_length=50, primary_key=True)
    created = fields.DatetimeField(auto_now_add= True)
    modified = fields.DatetimeField(auto_now= True)