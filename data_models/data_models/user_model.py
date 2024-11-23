from tortoise.models import Model
from tortoise import fields


class User(Model):
    """User model class for database table 'user'
    
    Inherits Model from tortoise.models
    Fields are required unless specified can be null
    Attributes:
        user_id: bigint Primary key. Auto created
        full_name: string for user full name. max length 50
        email: string for user email. Unique. max length 64
        google_user_id: string field to store google user id, if user uses google sign in. Can be null
        password_hash: binary field for user password hash. Can be null
        profile_pic: string field for link to user profile picture. max length 128. Can be null
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    user_id = fields.BigIntField(primary_key=True)
    full_name = fields.CharField(max_length=50)
    google_user_id = fields.CharField(null=True, unique=True, max_length=32)
    email = fields.CharField(max_length=64, unique=True)
    password_hash = fields.BinaryField(null=True)
    profile_pic = fields.CharField(max_length=128, null=True)
    created = fields.DatetimeField(auto_now_add= True)
    modified = fields.DatetimeField(auto_now= True)

class UserLlm(Model):
    """UserLlm model class for database table 'userllm'
    
    Inherits Model from tortoise.models
    Fields are required unless specified can be null
    Attributes:
        user_llm_id: bigint Primary key. Auto created
        user_llm_name: string for llm name provided by user. max length 50
        user_llm_description: string for llm description provided by user. max length 512
        llm: ForeignKey to llm table. Field name is llm_id
        user: ForeignKey to user table. Field name is user_id
        llm_config_cipher: binary field to store encrypted configuration to connect to LLM.
        kdf_salt: binary field to store kdf_salt for llm_config_cipher encryption.
        nonce: binary field to store nonce for llm_config_cipher encryption.
        auth_tag: binary field to store auth_tag for llm_config_cipher encryption.
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    user_llm_id = fields.BigIntField(primary_key=True)
    user_llm_name = fields.CharField(unique=True, max_length=50)
    user_llm_description = fields.TextField(max_length=512, null=True)
    bots_user_llm: fields.ReverseRelation['Bot'] # type: ignore
    llm = fields.ForeignKeyField('models.Llm', related_name='user_llm_id_name', on_delete=fields.NO_ACTION)
    user = fields.ForeignKeyField('models.User', related_name='user_llm_user')
    llm_config_cipher = fields.BinaryField()
    kdf_salt = fields.BinaryField()
    nonce = fields.BinaryField()
    auth_tag = fields.BinaryField()
    created = fields.DatetimeField(auto_now_add= True)
    modified = fields.DatetimeField(auto_now= True)