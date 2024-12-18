from app import create_quart_app
from app.config import Production
config=Production()
production_app = create_quart_app(app_config=config)