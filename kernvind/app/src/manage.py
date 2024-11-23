import logging
from app import create_app

from quart_schema import RequestSchemaValidationError, ResponseSchemaValidationError


def dev_app_generate_dbschemas():
    app = create_app(mode='Development')
    app.run(host=app.config['HOST'], port=app.config['PORT'])

def dev_app():
    app = create_app(mode='Development')
    
    @app.errorhandler(RequestSchemaValidationError)
    async def handle_request_validation_error(error):
        logging.error(f'quart schema request validation error: {str(error.validation_error)}')   
        return {
      "error": 'All required fields are not provided',
     }, 400
    
    @app.errorhandler(ResponseSchemaValidationError)
    async def handle_response_validation_error(error):
        logging.error(f'quart schema response validation error: {str(error.validation_error)}')   
        return {
      "error": 'Response validation failed',
     }, 500
    app.run(host=app.config['HOST'], port=app.config['PORT'])

production_app = create_app(mode='Production')