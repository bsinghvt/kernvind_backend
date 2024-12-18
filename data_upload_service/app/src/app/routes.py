from app.data_upload.controllers.playground_controller import dataupload_bp
from quart import Quart
def register_routes(app: Quart):
    app.register_blueprint(dataupload_bp, url_prefix='/dataupload')