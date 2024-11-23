from app.llm_chat.controllers.chat_controller import chat_bp
from quart import Quart
def register_routes(app: Quart):
    app.register_blueprint(chat_bp, url_prefix='/chat')