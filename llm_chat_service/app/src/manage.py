from app import create_app
from database import init_db


def dev_app():
    
    app = create_app(mode='Development')
    init_db(app=app, generate_schemas=True)
    app.run(host=app.config['HOST'], port=app.config['PORT'])

production_app = create_app(mode='Production')