from data_models.llm_model import LlmModelType, Llm

from data_models.datafeed_source_model import DataFeedSource

from data_models.datasource_model import DatafeedLoadStatus

async def createLlmModelTypes():
  try:
    llmTypes = ['Ollama', 'OpenAI']
    for lt in llmTypes:
      llmType = await LlmModelType.filter(llmmodeltype_name=lt).first()
      if not llmType:
        await LlmModelType.create(llmmodeltype_name=lt)
  except Exception as e:
    raise

async def createLlmModels():
  try:
    llmAndTypes = [
            ('llama3.1', 'Ollama'),
            ('gemma2:9b', 'Ollama'), 
            ('gpt-4o-mini', 'OpenAI'), 
            ('gpt-4o', 'OpenAI')
          ]
    for llmModelAndType in llmAndTypes:
      llm, llmType = llmModelAndType
      model = await Llm.filter(llm_name=llm, llmmodeltype_id=llmType).first()
      if not model:
        await Llm.create(llm_name=llm, llmmodeltype_id=llmType)
  except Exception as e:
    raise
  
async def createDatafeedSourceTypes():
  try:
    datafeedSources = [
            'Youtube video transcript',
            'Google drive'
          ]
    for datafeedSource in datafeedSources:
      df = await DataFeedSource.filter(datafeedsource_id=datafeedSource).first()
      if not df:
        await DataFeedSource.create(datafeedsource_id=datafeedSource)
  except Exception as e:
    raise
  
async def createDatafeedLoadStatuses():
  try:
    datafeedLoadStatuses = [
      'ERROR',
      'LOADED',
      'LOADING',
      'NEW',
      'REFRESH',
      ]
    for datafeedStatus in datafeedLoadStatuses:
      ds = await DatafeedLoadStatus.filter(datafeedloadstatus_id=datafeedStatus).first()
      if not ds:
        await DatafeedLoadStatus.create(datafeedloadstatus_id=datafeedStatus)
  except Exception as e:
    raise

async def loadInitialDatabaseData():
    await createLlmModelTypes()
    await createLlmModels()
    await createDatafeedSourceTypes()
    await createDatafeedLoadStatuses()
