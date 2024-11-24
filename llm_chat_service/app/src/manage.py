from app import create_app


def dev_app():
    
    app = create_app(mode='Development')
    app.run(host=app.config['HOST'], port=app.config['PORT'])