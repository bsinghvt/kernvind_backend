import pytest
from tortoise.contrib.test import finalizer
import pytest
from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError, OperationalError

def getTestDBConfig(app_label: str, modules: list) -> dict:
    return {
        "connections": {
            "default": "sqlite://:memory:",  # In-memory database for tests
        },
        "apps": {
            app_label: {
                "models": modules,
                "default_connection": "default",
            },
        },
    }

TORTOISE_MODELS = ["data_models.user_model",
                            "data_models.bot_model",
                            "data_models.llm_model",
                            "data_models.datasource_model",
                            "data_models.datafeed_source_model",
                            "data_models.chat_message_model",
                            "data_models.vector_model",]
 

# Define your Tortoise ORM configuration for tests
@pytest.mark.asyncio
@pytest.fixture(scope="module")
def db(event_loop):
    config = getTestDBConfig(app_label="models", modules=TORTOISE_MODELS)

    async def _init_db() -> None:
        await Tortoise.init(config)
        try:
            await Tortoise._drop_databases()
        except (DBConnectionError, OperationalError):  # pragma: nocoverage
            pass

        await Tortoise.init(config, _create_db=True)
        await Tortoise.generate_schemas(safe=False)

    event_loop.run_until_complete(_init_db())
    yield
    event_loop.run_until_complete(Tortoise._drop_databases())
    finalizer()