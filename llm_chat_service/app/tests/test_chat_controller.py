from datetime import datetime
from app.core.models.error_model import Failure
import pytest
from unittest.mock import patch, AsyncMock
from app.llm_chat.model.chat_message_model import ChatMessageOut
from app.llm_chat.model.bot_user_llm_model import BotUserLlm, LlmConfig
from app.llm_chat.services.broker import Broker
from quart_jwt_extended import create_access_token
from app import create_app
    
@pytest.fixture
def broker():
    return Broker()

@pytest.fixture
def app():
    return create_app(mode='Testing')

@pytest.mark.asyncio
async def test_websocket_handler_invalid_bot_id(app):
    """Test WebSocket handler with an invalid bot_id format."""
    async with app.app_context():
        client = app.test_client()
        access_token = create_access_token(identity=123, user_claims={"full_name": "Test User"})
        headers = [("Authorization", f"Bearer {access_token}")]
        async with client.websocket('chat/ws/bot/invalid_bot_id', headers=headers, subprotocols=["authorization", access_token]) as websocket:
            response = await websocket.receive_json()
            assert response['error'] == "Invalid bot_id format"

@pytest.mark.asyncio
async def test_websocket_handler_authorization_failed(app):
    """Test WebSocket handler with failed authorization."""
    async with app.app_context():
        client = app.test_client()
        headers = [("Authorization", "Bearer invalid_token")]
        async with client.websocket('chat/ws/bot/1', headers=headers, subprotocols=["authorization", "invalid_token"]) as websocket:
            response = await websocket.receive_json()
            assert response['error'] == "Not authorized"
        
@pytest.mark.asyncio
async def test_websocket_handler_missing_user_id_or_user_name(app):
    """Test WebSocket handler with missing user_id or user_name in JWT token."""
    async with app.app_context():
        client = app.test_client()
        access_token = create_access_token(identity=13, user_claims={"full_name": ''})
        headers = [("Authorization", f"Bearer {access_token}")]
        async with client.websocket('/chat/ws/bot/1', headers=headers, subprotocols=["authorization", access_token]) as websocket:
            response = await websocket.receive_json()
            assert response['error'] == "Not authorized"

@pytest.mark.asyncio
async def test_websocket_handler_no_llm_assigned(app):
    """Test WebSocket handler with no LLM assigned to the bot."""
    #async with app.app_context():
    client = app.test_client()
    access_token = {'identity':123,'iat': 23424, 'nbf':2342342, 'jti': 'qwerty', 'exp':232535, 'fresh': True, 'type': 'token', 'user_claims':{"full_name": "Test User"}}
    headers = [("Authorization", f"Bearer {access_token}")]
    mock_bot_user_llm = BotUserLlm(
        bot_id=1,
        llm_name="gpt-4",
        llmmodeltype_name="openai",
        user_llm_id=2,
        llm_config=LlmConfig(),
        datasource_id=10,
        datasource_name="test_datasource",
    )
    with patch("app.llm_chat.controllers.chat_controller.decode_jwt") as mock_decode_token ,\
        patch("app.llm_chat.controllers.chat_controller.get_bot_userllm", new=AsyncMock(return_value=mock_bot_user_llm)), \
        patch("app.llm_chat.controllers.chat_controller.get_lc_llm") as mock_get_lc_llm: 
        mock_decode_token.return_value = access_token
        mock_get_lc_llm.return_value = False
        async with client.websocket('/chat/ws/bot/1', headers=headers, subprotocols=["authorization", access_token]) as websocket:
            response = await websocket.receive_json()
            assert response['error'] == "LLM not assigned. Please check LLM configuration."

@pytest.mark.asyncio
async def test_websocket_handler_llm_assigned_no_config(app):
    """Test WebSocket handler with no LLM assigned to the bot."""
    #async with app.app_context():
    client = app.test_client()
    access_token = {'identity':123,'iat': 23424, 'nbf':2342342, 'jti': 'qwerty', 'exp':232535, 'fresh': True, 'type': 'token', 'user_claims':{"full_name": "Test User"}}
    headers = [("Authorization", f"Bearer {access_token}")]
    mock_bot_user_llm = BotUserLlm(
        bot_id=1,
        llm_name="gpt-4",
        llmmodeltype_name="openai",
        user_llm_id=2,
        llm_config=LlmConfig(),
        datasource_id=10,
        datasource_name="test_datasource",
    )
    with patch("app.llm_chat.controllers.chat_controller.decode_jwt") as mock_decode_token ,\
        patch("app.llm_chat.controllers.chat_controller.get_bot_userllm", new=AsyncMock(return_value=mock_bot_user_llm)), \
        patch("app.llm_chat.controllers.chat_controller.get_lc_llm") as mock_get_lc_llm:
        mock_get_lc_llm.return_value = True  
        mock_decode_token.return_value = access_token
        
        async with client.websocket('/chat/ws/bot/1', headers=headers, subprotocols=["authorization", access_token]) as websocket:
            response = await websocket.receive_json()
            assert response['error'] == "Cannot connect to LLM. Please check LLM configuration."

@pytest.mark.asyncio
async def test_websocket_handler_no_user_llm(app):
    """Test WebSocket handler with no LLM assigned to the bot."""
    #async with app.app_context():
    client = app.test_client()
    access_token = {'identity':123,'iat': 23424, 'nbf':2342342, 'jti': 'qwerty', 'exp':232535, 'fresh': True, 'type': 'token', 'user_claims':{"full_name": "Test User"}}
    headers = [("Authorization", f"Bearer {access_token}")]
    with patch("app.llm_chat.controllers.chat_controller.decode_jwt") as mock_decode_token ,\
        patch("app.llm_chat.controllers.chat_controller.get_bot_userllm", new=AsyncMock(return_value=(Failure(error="Failed to get bot-user LLM: "), 501))) as mock_get_bot_userllm:
        mock_decode_token.return_value = access_token
        async with client.websocket('/chat/ws/bot/1', headers=headers, subprotocols=["authorization", access_token]) as websocket:
            response = await websocket.receive_json()
            assert 'Failed to get bot-user LLM: ' in response['error']
            
@pytest.mark.asyncio
async def test_websocket_handler_no_data_source(app):
    """Test WebSocket handler with no LLM assigned to the bot."""
    #async with app.app_context():
    client = app.test_client()
    access_token = {'identity':123,'iat': 23424, 'nbf':2342342, 'jti': 'qwerty', 'exp':232535, 'fresh': True, 'type': 'token', 'user_claims':{"full_name": "Test User"}}
    headers = [("Authorization", f"Bearer {access_token}")]
    mock_bot_user_llm = BotUserLlm(
        bot_id=1,
        llm_name="gpt-4",
        llmmodeltype_name="openai",
        user_llm_id=2,
        llm_config=LlmConfig(),
        datasource_id=None,
        datasource_name=None,
    )
    date_time_now = datetime.now()
    msg = ChatMessageOut(
            message_id='12345',
            bot_id=2,
            user_id_in=2,  # Message for user 2 in bot 2
            message_text="Broadcast message to bot 2",
            notification=True,
            created=date_time_now,
            modified=date_time_now,
        )
    async def mock_subscribe(bot_id, user_id):
        yield msg
        
    with patch("app.llm_chat.controllers.chat_controller.decode_jwt") as mock_decode_token ,\
        patch("app.llm_chat.controllers.chat_controller.get_bot_userllm", new=AsyncMock(return_value=mock_bot_user_llm)), \
        patch("app.llm_chat.controllers.chat_controller.get_lc_llm") as mock_get_lc_llm,\
        patch("app.llm_chat.controllers.chat_controller.test_llm") as mock_test_llm,\
        patch("app.llm_chat.services.get_pgvector_instance_service") as mock_get_pgvector_instance,\
        patch("app.llm_chat.controllers.chat_controller._receive", new=AsyncMock()) as mock_receive_function ,\
        patch("app.llm_chat.controllers.chat_controller.broker.subscribe", mock_subscribe) as mock_sub:
        mock_get_lc_llm.return_value = True  
        mock_decode_token.return_value = access_token
        mock_test_llm.return_value = 'test'
        async with client.websocket('/chat/ws/bot/1', headers=headers, subprotocols=["authorization", access_token]) as websocket:
            await websocket.send_json(msg.model_dump())
            websocket.send_as = AsyncMock()
            resp = await websocket.receive_json()
            
            mock_get_pgvector_instance.assert_not_called()
            mock_receive_function.assert_called_once_with(bot_id=1,
                                                        user_name=access_token['user_claims']['full_name'],
                                                        user_id=access_token['identity'],
                                                        llm=f'{mock_bot_user_llm.llmmodeltype_name}-{mock_bot_user_llm.llm_name}',
                                                        datasource_id=mock_bot_user_llm.datasource_id,
                                                        )
            assert resp['message_text'] == 'Broadcast message to bot 2'

@pytest.mark.asyncio
async def test_websocket_handler_with_data_source(app):
    """Test WebSocket handler with no LLM assigned to the bot."""
    #async with app.app_context():
    client = app.test_client()
    access_token = {'identity':123,'iat': 23424, 'nbf':2342342, 'jti': 'qwerty', 'exp':232535, 'fresh': True, 'type': 'token', 'user_claims':{"full_name": "Test User"}}
    headers = [("Authorization", f"Bearer {access_token}")]
    mock_bot_user_llm = BotUserLlm(
        bot_id=1,
        llm_name="gpt-4",
        llmmodeltype_name="openai",
        user_llm_id=2,
        llm_config=LlmConfig(),
        datasource_id=1,
        datasource_name='test_datasource',
    )
    date_time_now = datetime.now()
    msg = ChatMessageOut(
            message_id='12345',
            bot_id=2,
            user_id_in=2,  # Message for user 2 in bot 2
            message_text="Broadcast message to bot 2",
            notification=True,
            created=date_time_now,
            modified=date_time_now,
        )
    async def mock_subscribe(bot_id, user_id):
        yield msg

    with patch("app.llm_chat.controllers.chat_controller.decode_jwt") as mock_decode_token ,\
        patch("app.llm_chat.controllers.chat_controller.get_bot_userllm", new=AsyncMock(return_value=mock_bot_user_llm)) as mock_get_bot_userllm, \
        patch("app.llm_chat.controllers.chat_controller.get_lc_llm") as mock_get_lc_llm,\
        patch("app.llm_chat.controllers.chat_controller.test_llm") as mock_test_llm,\
        patch("app.llm_chat.controllers.chat_controller.get_pgvector_instance") as mock_get_pgvector_instance,\
        patch("app.llm_chat.controllers.chat_controller._receive", new=AsyncMock()) as mock_receive_function ,\
        patch("app.llm_chat.controllers.chat_controller.broker.subscribe", mock_subscribe) as mock_sub:
        mock_get_lc_llm.return_value = True  
        mock_decode_token.return_value = access_token
        mock_test_llm.return_value = 'test'
        async with client.websocket('/chat/ws/bot/1', headers=headers, subprotocols=["authorization", access_token]) as websocket:
            await websocket.send_json(msg.model_dump())
            websocket.send_as = AsyncMock()
            resp = await websocket.receive_json()
            mock_get_pgvector_instance.assert_called_once_with(datasource_id = mock_bot_user_llm.datasource_id,
                                                                datasource_name=mock_bot_user_llm.datasource_name,
                                                                bot_id=1)
            mock_receive_function.assert_called_once_with(bot_id=1,
                                                        user_name=access_token['user_claims']['full_name'],
                                                        user_id=access_token['identity'],
                                                        llm=f'{mock_bot_user_llm.llmmodeltype_name}-{mock_bot_user_llm.llm_name}',
                                                        datasource_id=mock_bot_user_llm.datasource_id,
                                                        )
            assert resp['message_text'] == 'Broadcast message to bot 2'
            

            
