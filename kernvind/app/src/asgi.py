from app.config import Production
from app import create_app
config = Production()
production_app = create_app(app_config=config)