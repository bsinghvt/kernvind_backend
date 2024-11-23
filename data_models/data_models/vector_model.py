from tortoise.models import Model
from tortoise import fields

class langchain_pg_collection(Model):
    """langchain_pg_collection model class for database table 'langchain_pg_collection'
    
    Inherits Model from tortoise.models
    Fields are required unless specified can be null
    Attributes:
        uuid: UUID Primary key. 
        name: string for user name. Unique. max length 64
        cmetadata: Json field for any metadata.
    """
    uuid = fields.UUIDField(primary_key=True)
    name = fields.CharField(max_length=64, unique=True)
    cmetadata = fields.JSONField(null=True)
    

class langchain_pg_embedding(Model):
    """langchain_pg_embedding model class for database table 'langchain_pg_embedding'
    
    Inherits Model from tortoise.models
    Fields are required unless specified can be null
    Attributes:
        id: varying Primary key. 
        collection: UUID. foriegn key to langchain_pg_collection, actual field is collection_id
        document: varying field for any documents.
        cmetadata: Json field for any metadata.
    """
    id = fields.TextField(primary_key=True)
    collection = fields.ForeignKeyField('models.langchain_pg_collection', related_name='pg_collection')
    document = fields.TextField()
    cmetadata = fields.JSONField(null=True)