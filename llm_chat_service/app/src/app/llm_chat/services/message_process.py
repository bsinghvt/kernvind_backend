from datetime import datetime
from typing import List, Optional, Tuple

from .broker import Broker

from .save_message_service import save_message

from .llm import runllm_with_rag
from ..model.chat_message_model import ChatMessageDatabase, ChatMessageIn, ChatMessageOut


def create_chat_message_out(
    message_id: str,
    bot_id: int,
    user_id_in: int,
    user_id_out: Optional[int],
    message_text: str,
    created: datetime,
    modified: datetime,
    user_name: Optional[str] = None,
    notification: bool = False,
) -> ChatMessageOut:
    """Helper to create ChatMessageOut objects."""
    return ChatMessageOut(
        message_id=message_id,
        bot_id=bot_id,
        user_id_in=user_id_in,
        user_id_out=user_id_out,
        message_text=message_text,
        notification=notification,
        created=created,
        modified=modified,
        message_user_name=user_name,
    )


async def process_llm_response(
    broker: Broker,
    incoming_message: ChatMessageIn,
    bot_id: int,
    user_id: int,
    datasource_id: Optional[int],
    llm: str,
    outgoing_message_id: str,
    now: datetime,
) -> None:
    """Process the message with the LLM and publish responses."""
    response = runllm_with_rag(incoming_message.message_text, bot_id)
    question_and_answer: Tuple[str, List[str]] = (incoming_message.message_text, [])
    async for chunk in response:
        message_chunk = create_chat_message_out(
            message_id=outgoing_message_id,
            bot_id=incoming_message.bot_id,
            user_id_in=user_id,
            user_id_out=None,
            message_text=chunk,
            created=now,
            modified=now,
        )
        await broker.publish(message_chunk)
        question_and_answer[1].append(chunk)

    # Save the response to the database
    if question_and_answer[1]:
        bot_answer = "".join(question_and_answer[1])
        if "I don't have enough information to answer this question" not in bot_answer:
            await save_message(
                ChatMessageDatabase(
                    user_message=question_and_answer[0],
                    notification=incoming_message.notification,
                    bot_answer=bot_answer,
                    user_id=user_id,
                    bot_id=bot_id,
                    datasource_id=datasource_id,
                    llm=llm,
                )
            )