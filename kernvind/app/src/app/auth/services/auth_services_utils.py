from data_models.user_model import User
from quart_jwt_extended import (
    create_access_token,
    create_refresh_token,
)

from ...core.models.user_claims_model import UserClaims

def create_access_token_util(user: User):
    try:
        user_claims = UserClaims(full_name=user.full_name).model_dump()
        access_token = create_access_token(identity=user.user_id, user_claims=user_claims)
        return access_token
    except:
        raise
    

def create_refresh_token_util(user: User):
    try:
        user_claims = UserClaims(full_name=user.full_name).model_dump()
        refresh_token = create_refresh_token(identity=user.user_id, user_claims=user_claims)
        return refresh_token
    except:
        raise