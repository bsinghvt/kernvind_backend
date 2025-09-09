from app.config import Development
from app import create_app


def dev_app():
    config=Development()
    app = create_app(app_config=config)
    app.run(host=app.config['HOST'], port=app.config['PORT'])