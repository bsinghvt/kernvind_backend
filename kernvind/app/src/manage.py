from app import create_app
from app.config import Development


def dev_app_generate_dbschemas():
    config=Development()
    app = create_app(app_config=config)
    app.run(host=app.config['HOST'], port=app.config['PORT'])

def dev_app():
    config=Development()
    app = create_app(app_config=config)
    app.run(host=app.config['HOST'], port=app.config['PORT'])

