from tortoise.models import Model
from tortoise import fields

class ChatMessage(Model):
    """ChatMessage model class for database table 'chatmodel'
    
    Inherits Model from tortoise.models
    Fields are required unless specified can be null
    Attributes:
        chat_message_id: bigint Primary key. Auto created
        user_message: string for user message text
        is_notification: bool for if the message is just a notification, default is NULL
        is_bot_question: bool for if the message is question for bot, default is True
        bot_answer: string for bot answer text
        datasource: ForeignKey to datasource table. Field name is datasource_id
        bot: ForeignKey to bot table. Field name is bot_id
        user: ForeignKey to user table. Field name is user_id
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    chat_message_id = fields.BigIntField(primary_key=True)
    user_message = fields.TextField()
    is_notification = fields.BooleanField(null=True, db_index=True)
    is_bot_question = fields.BooleanField(default=True, db_index=True)
    bot_answer = fields.TextField(null=True)
    llm = fields.CharField(max_length=50)
    datasource = fields.ForeignKeyField('models.DataSource', related_name='datasource_chat_mesage', db_index=True, null=True)
    bot = fields.ForeignKeyField('models.Bot', related_name='bot_chat_mesage', db_index=True)
    user = fields.ForeignKeyField('models.User', related_name='user_chat_mesage')
    created = fields.DatetimeField(auto_now_add = True)
    modified = fields.DatetimeField(auto_now = True, db_index=True)