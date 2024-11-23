import logging
from data_models.user_model import User

from .auth_services_utils import create_access_token_util, create_refresh_token_util
from ..models.api_models import AuthFailure, AuthSuccess, Login, SignUp
from quart_bcrypt import async_generate_password_hash, async_check_password_hash
from tortoise.exceptions import IntegrityError


async def user_signup(sign_up: SignUp):
    """Use case to sign up user

    Args:
        sign_up (SignUp): A SignUp api model object

    Returns:
        (tuple[AuthSuccess, Literal[201]] | tuple[AuthFailure, Literal[409]] | tuple[AuthFailure, Literal[500]])
    """
    password_hash = await async_generate_password_hash(password=sign_up.password)
    try:
        new_user = await User.create(full_name = sign_up.full_name, email=sign_up.email, password_hash=password_hash)
        access_token = create_access_token_util(user=new_user)
        refresh_token = create_refresh_token_util(user=new_user)
        logging.info(f'user {sign_up.email} signed up successfully')
        return AuthSuccess(token=access_token, 
                            refresh_token=refresh_token), 201
    except IntegrityError:
        logging.error(f'user {sign_up.email} tried duplicate email sign up')
        return AuthFailure(error="Email already exists"), 409
    except Exception as e:
        logging.critical(e.__str__())
        return AuthFailure(error="Something went wrong. Please try again"), 500
    


async def user_login(login: Login):
    """Use case to login user

    Args:
        login (Login): Login model

    Returns:
        (tuple[AuthFailure, Literal[401]] | tuple[AuthSuccess, Literal[200]] | tuple[AuthFailure, Literal[500]])
    """
    try:
        userList = await User.filter(email=login.email)
        
        if len(userList) == 0 or len(userList) > 1:
            logging.error(f'user {login.email} entered wrong email')
            return AuthFailure(error="Wrong Email or Password. Please try again"), 401
        password_hash = userList[0].password_hash

        password_match = await async_check_password_hash(pw_hash=password_hash, password=login.password)
        if password_match:
            access_token = create_access_token_util(user=userList[0])
            refresh_token = create_refresh_token_util(user=userList[0])
            logging.info(f'user {login.email} logged in successfully')
            return AuthSuccess(token=access_token,
                                refresh_token=refresh_token), 200
        else:
            logging.error(f'user {login.email} entered wrong password {login.password}')
        
        return AuthFailure(error="Wrong Email or Password. Please try again"), 401
    except Exception as e:
        logging.critical(e.__str__())
        return AuthFailure(error="Something went very wrong. Please try again"), 500