from .auth.controllers.login_controller import login_bp
from .auth.controllers.signup_controller import signup_bp
from .auth.controllers.social_auth_controller import social_auth_bp
from .bot.controllers.bot_controller import bot_bp
from .user_llm.controllers.user_llm_controller import user_llm_bp
from .user_llm.controllers.llm_list_controller import public_llm_bp
from .datasource.controllers.datasource_controller import datasource_bp
from .dataupload.controllers.dataupload_playground_controller import dataupload_bp

from quart import Quart
def register_routes(app: Quart):
    app.register_blueprint(social_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(signup_bp, url_prefix='/api/auth')
    app.register_blueprint(login_bp, url_prefix='/api/auth')
    app.register_blueprint(bot_bp, url_prefix='/api/bot')
    app.register_blueprint(user_llm_bp, url_prefix='/api/userllm')
    app.register_blueprint(public_llm_bp, url_prefix='/api/publicllm')
    app.register_blueprint(datasource_bp, url_prefix='/api/datasource') 
    app.register_blueprint(dataupload_bp, url_prefix='/api/dataupload') 