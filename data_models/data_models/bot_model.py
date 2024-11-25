from tortoise.models import Model
from tortoise import fields

class DataSource(Model):
    """DataSource model class for database table 'datasource'
    
    Inherits Model from tortoise.models
    Fields are required unless specified can be null
    This table holds the information about datasource which is fed to bot

    Attributes:
        datasource_id: bigint Primary key. Auto created
        datasource_name: string for name. Unique. max length 64
        datasource_description: string field description. max length 1024. Can be null
        created_by_user: ForeignKey to user table
        bot_datasource: reverse relation to bot table
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    datasource_id = fields.BigIntField(primary_key=True)
    datasource_name = fields.CharField(max_length=64, unique=True)
    datasource_description = fields.CharField(max_length=1024, null=True)
    created_by_user = fields.ForeignKeyField('models.User', related_name='datasource_created_by_user')
    bot_datasource: fields.ReverseRelation["Bot"]
    created = fields.DatetimeField(auto_now_add= True)
    modified = fields.DatetimeField(auto_now= True)
    
class Bot(Model):
    """Bot model class for database table 'bot'
    
    Inherits Model from tortoise.models
    Fields are required unless specified can be null
    
    Attributes:
        bot_id: bigint Primary key. Auto created
        bot_name: string for name. Unique. max length 64
        bot_description: string field for description. max length 1024. Can be null
        user_llm: ForeignKey to userllm table. Field in table is user_llm_id
        created_by_user: ForeignKey to user table. Field in table is created_by_user_id
        datasource: ForeignKey to datasource table. Field in table is datasource_id
        bot_users: many to many relation field between user and bot using botuserxref table
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    bot_id = fields.BigIntField(primary_key=True)
    bot_name = fields.CharField(max_length=64, unique=True)
    bot_description = fields.CharField(max_length=1024, null=True)
    user_llm  = fields.ForeignKeyField('models.UserLlm', related_name='bots_user_llm', on_delete=fields.NO_ACTION)
    created_by_user = fields.ForeignKeyField('models.User', related_name='created_by_user')
    datasource = fields.ForeignKeyField('models.DataSource', related_name='bot_datasource', on_delete=fields.SET_NULL, null=True)
    """
    datasource: fields.OneToOneRelation[DataSource] = fields.OneToOneField(model_name="models.DataSource", 
                                                                            null=True,
                                                                            on_delete=fields.OnDelete.SET_NULL, 
                                                                            related_name="bot_datasource",
                                                                            to_field='datasource_id') # type: ignore
    """
    bot_users = fields.ManyToManyField('models.User', through='botuserxref')
    created = fields.DatetimeField(auto_now_add= True)
    modified = fields.DatetimeField(auto_now= True)
    
class BotUserXref(Model):
    """BotUserXref model class for database table 'botuserxref'
    
    Fields are required unless specified can be null
    'botuserxref' table holds many to many relation between user and bot
    Inherits Model from tortoise.models

    Attributes:
        botuserxref_id: bigint Primary key. Auto created
        user: ForeignKey to user table
        bot: ForeignKey to bot table
        added_by_user: ForeignKey to user table. User which added a ew user to bot
        can_add_users: Boolean field to check if user can add new users to bot. Default is false
        can_change_datasource: Boolean field to check if user can change datasource for bot. Default is false
        can_change_datasourcefeed: Boolean field to check if user can change or add datasource feed for bot data source. Default is false
        can_see_datasourcefeed: Boolean field to check if user can see datasource feed for bot data source. Default is false
        can_see_datasource: Boolean field to check if user can see datasource for bot. Default is false
        can_change_llm: Boolean field to check if user can change llm for bot. Default is false
        can_see_llm: Boolean field to check if user can see llm for bot. Default is false
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    botuserxref_id = fields.BigIntField(primary_key=True)
    bot = fields.ForeignKeyField('models.Bot')
    user = fields.ForeignKeyField('models.User')
    can_add_users=fields.BooleanField(default=False)
    can_change_datasource=fields.BooleanField(default=False)
    can_see_datasource=fields.BooleanField(default=False)
    can_see_datasourcefeed=fields.BooleanField(default=False)
    can_change_datasourcefeed=fields.BooleanField(default=False)
    can_see_llm=fields.BooleanField(default=False)
    can_change_llm=fields.BooleanField(default=False)
    added_by_user = fields.ForeignKeyField('models.User', related_name='added_by_user',null=True, on_delete=fields.SET_NULL)
    created = fields.DatetimeField(auto_now_add= True)
    modified = fields.DatetimeField(auto_now= True)
    class Meta: # type: ignore
        unique_together=(('bot','user'))
            
