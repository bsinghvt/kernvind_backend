from tortoise.models import Model
from tortoise import fields


class DataFeed(Model):
    """DataFeed model class for database table 'datafeed'
    
    Fields are required unless specified can be null
    Inherits Model from tortoise.models
    This table holds the information about data feeds to which datasource table points

    Attributes:
        datafeed_id: bigint Primary key. Auto created
        datafeed_name: string for name. Unique. max length 64
        datafeed_source_unique_id: string field for unique datasource id for a given user e.g youtube URL. max length 256.
        datafeed_source_title: string field for title e.g youtube title, google drive folder name. max length 512.
        lastload_datetime: datetime field default to null timestamp based on last loaded data timestamp
        datafeed_description: string field description. max length 1024. Can be null
        datafeedsource: ForeignKey to DataFeedSource table. Actual field is datafeedsource_id
        datasource: ForeignKey to DataSource table. Actual field is datasource_id
        datafeedsource_config_cipher: Binary field to store encrypted configuration to connect to data feed source.
        kdf_salt: binary field to store kdf_salt for datafeedsource_config_cipher encryption.
        nonce: binary field to store nonce for datafeedsource_config_cipher encryption.
        auth_tag: binary field to store auth_tag for datafeedsource_config_cipher encryption.
        created_by_user: ForeignKey to user table
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    datafeed_id = fields.BigIntField(primary_key=True)
    datafeed_name = fields.CharField(max_length=64, unique=True)
    datafeed_source_unique_id = fields.CharField(max_length=256)
    datafeed_source_title =  fields.CharField(max_length=512)
    lastload_datetime = fields.DatetimeField(null = True)
    datafeedloadstatus = fields.ForeignKeyField(model_name='models.DatafeedLoadStatus', related_name='datafeedloadstatus', default='NEW',  db_index=True, on_delete=fields.NO_ACTION)
    datafeed_description = fields.CharField(max_length=1024, null=True)
    datafeedsource = fields.ForeignKeyField('models.DataFeedSource', related_name='datafeedsource', on_delete=fields.NO_ACTION)
    datasource = fields.ForeignKeyField('models.DataSource', related_name='datasource_datafeed')
    datafeedsource_config_cipher = fields.BinaryField(null = True)
    kdf_salt = fields.BinaryField(null = True)
    nonce = fields.BinaryField(null = True)
    auth_tag = fields.BinaryField(null = True)
    created_by_user = fields.ForeignKeyField('models.User', related_name='feed_created_by_user')
    created = fields.DatetimeField(auto_now_add = True)
    modified = fields.DatetimeField(auto_now = True, db_index=True)
    
    class Meta: # type: ignore
        unique_together=(('datafeed_source_unique_id','datafeedsource','created_by_user','datasource'))
    
class DatafeedLoadStatus(Model):
    """DatafeedLoadStatus model class 
    
    Fields are required unless specified can be null
    Inherits Model from tortoise.models

    Attributes:
        datafeedsource_id: string for load status. max length 16
        created: datetime field default to current timestamp during record creation
        modified: datetime field default to current timestamp during record update and creation
    """
    datafeedloadstatus_id = fields.CharField(max_length=16, primary_key=True)
    created = fields.DatetimeField(auto_now_add= True)
    modified = fields.DatetimeField(auto_now= True)