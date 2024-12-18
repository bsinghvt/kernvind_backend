import logging
from data_models.user_model import User
from quart import current_app
from ..models.google_sign_in_model import GoogleSigIn, GoogleSignInIdToken
from .auth_services_utils import create_access_token_util, create_refresh_token_util
from ..models.api_models import AuthFailure, AuthSuccess
from google.oauth2 import id_token
from google.auth.transport import requests


async def user_google_login(login: GoogleSigIn):
    """Use case to google login user

    Args:
        login (GoogleSigIn): GoogleSigIn model

    Returns:
        (tuple[AuthFailure, Literal[401]] | tuple[AuthSuccess, Literal[200]] | tuple[AuthFailure, Literal[500]])
    """
    try:
        id_token_jwt = login.id_token
        platform = login.platform
        client_id = ''
        if platform == 'web':
            client_id = current_app.config['GOOGLE_SIGN_IN_WEB_CLIENT_ID']
        elif platform == 'ios':
            client_id = current_app.config['GOOGLE_SIGN_IN_WEB_CLIENT_ID']
        elif platform == 'android':
            client_id = current_app.config['GOOGLE_SIGN_IN_ANDROID_WEB_CLIENT_ID']
        
        if client_id == '':
            return AuthFailure(error="Required parameters are missing. Please try again"), 400
        user_info_dict = id_token.verify_oauth2_token(id_token_jwt, requests.Request(), client_id)
        user_info = GoogleSignInIdToken.model_validate(user_info_dict)
        if user_info.email_verified != True:
            return AuthFailure(error="Google email is not verified"), 401
        userList = await User.filter(google_user_id=user_info.sub)
        
        if len(userList) == 1:
            access_token = create_access_token_util(user=userList[0])
            refresh_token = create_refresh_token_util(user=userList[0])
            await User.filter(google_user_id=user_info.sub).update(full_name=user_info.name,
                                                                            email=user_info.email,
                                                                            profile_pic=user_info.picture)
            logging.info(f'user {user_info.email} logged in successfully using google sign in')
            return AuthSuccess(token=access_token,
                                refresh_token=refresh_token), 200
        elif len(userList) > 1:
            logging.critical(f'user {user_info.email} returned more than 1 row from user tabele using google user id: {user_info.sub}')
            return AuthFailure(error="Something went wrong. Please try again"), 500
        
        new_user = await User.create(full_name = user_info.name, 
                                        email=user_info.email, 
                                        profile_pic=user_info.picture,
                                        google_user_id=user_info.sub)
        access_token = create_access_token_util(user=new_user)
        refresh_token = create_refresh_token_util(user=new_user)
        logging.info(f'user {user_info.email} signed up successfully using google sign in')
        return AuthSuccess(token=access_token, 
                            refresh_token=refresh_token), 201
        
    except Exception as e:
        logging.critical(e.__str__())
        return AuthFailure(error="Something went wrong. Please try again"), 500