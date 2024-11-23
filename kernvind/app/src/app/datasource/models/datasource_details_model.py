from typing import List



from pydantic import BaseModel

from .get_datasource_list_model import DataSourceList

from .new_datasource_models import DataSourceFeed


    
class DatasourceDetails(BaseModel):
    datasource: DataSourceList
    datafeeds: List[DataSourceFeed]