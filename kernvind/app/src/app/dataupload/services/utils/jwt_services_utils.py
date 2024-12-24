from quart_jwt_extended import (
    create_access_token,
)

def create_access_token_util(identity: str):
    try:
        access_token = create_access_token(identity=identity)
        return access_token
    except:
        raise
