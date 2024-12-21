from datetime import datetime
import uuid
import pytest
import asyncio
from collections import defaultdict
from app.llm_chat.services.broker import Broker
from app.llm_chat.model.chat_message_model import ChatMessageOut

date_time_now = datetime.now()

@pytest.fixture
def broker():
    """Fixture to provide a fresh Broker instance for each test."""
    return Broker()

@pytest.mark.asyncio
async def test_subscribe_and_publish_single_user(broker):
    """Test if a single user can subscribe and receive published messages."""
    bot_id = 1
    user_id = 1
    in_id = str(uuid.uuid4())
    sent_id = str(uuid.uuid4())
    message = ChatMessageOut(message_id=sent_id, 
                                            bot_id=bot_id,
                                            user_id_in=user_id,
                                            message_text="User is removed from bot",
                                            notification=True,
                                            created=date_time_now,
                                            modified=date_time_now)

    async def user_subscriber():
        async for msg in broker.subscribe(bot_id, user_id):
            assert msg.message_id == message.message_id
            assert msg.bot_id == message.bot_id
            assert msg.user_id_in == message.user_id_in
            assert msg.message_text == message.message_text
            assert msg.notification == message.notification
            assert msg.created == message.created
            assert msg.modified == message.modified
            break  # Exit after receiving the first message

    subscriber_task = asyncio.create_task(user_subscriber())
    await asyncio.sleep(0.1)  # Allow subscription setup
    await broker.publish(message)
    await asyncio.sleep(0.1)  # Allow message to propagate
    subscriber_task.cancel()

@pytest.mark.asyncio
async def test_subscribe_and_publish_multiple_users(broker):
    """Test if multiple users can subscribe and receive published messages."""
    # Setup
    bot_id = 1
    user_ids = [1, 2, 3]
    sent_id = str(uuid.uuid4())

    # Create message
    message = ChatMessageOut(
        message_id=sent_id,
        bot_id=bot_id,
        user_id_in=1,  # Not specific to any user
        message_text="Broadcast message to all users",
        notification=True,
        created=date_time_now,
        modified=date_time_now,
    )

    # Define a subscriber function
    async def user_subscriber(user_id, received_messages):
        """Subscribe to a bot and store received messages."""
        async for msg in broker.subscribe(bot_id, user_id):
            received_messages[user_id].append(msg)
            if msg.message_id == message.message_id:
                break  # Exit after receiving the expected message

    # Dictionary to track messages received by each user
    received_messages = {user_id: [] for user_id in user_ids}

    # Create subscriber tasks for all users
    subscriber_tasks = [
        asyncio.create_task(user_subscriber(user_id, received_messages))
        for user_id in user_ids
    ]

    # Allow subscription setup
    await asyncio.sleep(0.1)

    # Publish the message
    await broker.publish(message)

    # Wait for all subscribers to receive the message
    await asyncio.gather(*subscriber_tasks, return_exceptions=True)

    # Verify each user received the message
    for user_id in user_ids:
        assert len(received_messages[user_id]) == 1
        received_msg = received_messages[user_id][0]
        assert received_msg.message_id == message.message_id
        assert received_msg.bot_id == message.bot_id
        assert received_msg.message_text == message.message_text
        assert received_msg.notification == message.notification
        assert received_msg.created == message.created
        assert received_msg.modified == message.modified




@pytest.mark.asyncio
async def test_subscription_cleanup(broker):
    """Test if a user's subscription is properly cleaned up after cancellation."""
    bot_id = "bot1"
    user_id = "user1"

    async def user_subscriber():
        async for _ in broker.subscribe(bot_id, user_id):
            pass

    subscriber_task = asyncio.create_task(user_subscriber())
    await asyncio.sleep(0.1)  # Allow subscription setup
    subscriber_task.cancel()
    await asyncio.sleep(0.1)  # Allow cancellation to propagate

    assert user_id not in broker.websocket_bots[bot_id]
    
import logging
from unittest.mock import patch

@pytest.mark.asyncio
async def test_multiple_bots(broker):
    """Test if users subscribed to different bots receive the correct messages."""
    bot_ids = [1, 2]
    sent_ids = [str(uuid.uuid4()) for _ in bot_ids]  # Create unique message IDs for each bot
    
    # Define messages for each bot
    messages = {
        1: ChatMessageOut(
            message_id=sent_ids[0],
            bot_id=1,
            user_id_in=1,  # Message for user 1 in bot 1
            message_text="Broadcast message to bot 1",
            notification=True,
            created=date_time_now,
            modified=date_time_now,
        ),
        2: ChatMessageOut(
            message_id=sent_ids[1],
            bot_id=2,
            user_id_in=2,  # Message for user 2 in bot 2
            message_text="Broadcast message to bot 2",
            notification=True,
            created=date_time_now,
            modified=date_time_now,
        )
    }

    # To store the received messages for each bot and user
    received_messages = defaultdict(list)

    # Subscriber function to listen for messages
    async def user_subscriber(bot_id, user_id):
        async for msg in broker.subscribe(bot_id, user_id):
            received_messages[bot_id].append(msg)
            break  # Exit after receiving the message

    # Create tasks to simulate subscriptions for each user and bot
    tasks = []
    for bot_id in bot_ids:
        tasks.append(asyncio.create_task(user_subscriber(bot_id, bot_id)))  # Using bot_id as user_id

    # Allow time for subscriptions to set up
    await asyncio.sleep(0.1)

    # Publish the messages to each bot
    for bot_id, message in messages.items():
        await broker.publish(message)

    # Allow time for messages to propagate
    await asyncio.sleep(0.1)

    # Cancel the subscriber tasks after receiving messages
    for task in tasks:
        task.cancel()

    # Verify that each bot's subscribers received the correct message
    assert received_messages[1][0] == messages[1]
    assert received_messages[2][0] == messages[2]
