from logging.handlers import RotatingFileHandler

import boto3
from .config import Config
import watchtower, logging, os

def logger_set(config: Config):
    if not os.path.exists(config.LOGDIR):
        os.makedirs(config.LOGDIR)
    boto3_client=boto3.client('logs', config.AWS_REGION)  
    formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(name)s-%(filename)s-%(lineno)d-%(message)s')
    app_log_handler = logging.getLogger()
    if config.AWS_CLOUDWATCH_LOG_GROUP:
        handler = watchtower.CloudWatchLogHandler(log_group_name=config.AWS_CLOUDWATCH_LOG_GROUP + '_error', 
                                                stream_name=config.AWS_CLOUDWATCH_LOG_STREAM, 
                                                log_group_retention_days=config.AWS_CLOUDWATCH_LOG_RETENTION_DAYS, boto3_client=boto3_client)
    else:
        handler = RotatingFileHandler(f'{config.LOGDIR}/log.error', maxBytes=1024*1024, backupCount=5, encoding='utf-8')
        
    handler.setLevel(logging.ERROR)
    handler.setFormatter(formatter)
    
    app_log_handler.addHandler(handler)
    
    if config.AWS_CLOUDWATCH_LOG_GROUP:
        handler = watchtower.CloudWatchLogHandler(log_group_name=config.AWS_CLOUDWATCH_LOG_GROUP + '_info', 
                                                stream_name=config.AWS_CLOUDWATCH_LOG_STREAM, 
                                                log_group_retention_days=config.AWS_CLOUDWATCH_LOG_RETENTION_DAYS, boto3_client=boto3_client)
    else:
        handler = RotatingFileHandler(f'{config.LOGDIR}/log.info', maxBytes=1024*1024, backupCount=5, encoding='utf-8')
        
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)

    app_log_handler.addHandler(handler)
    app_log_handler.setLevel(logging.INFO)

    pgvector_logger = logging.getLogger('pgvector_logger')
    if config.AWS_CLOUDWATCH_LOG_GROUP:
        handler = watchtower.CloudWatchLogHandler(log_group_name=config.AWS_CLOUDWATCH_LOG_GROUP + '_pgvector_logger', 
                                                stream_name=config.AWS_CLOUDWATCH_LOG_STREAM, 
                                                log_group_retention_days=config.AWS_CLOUDWATCH_LOG_RETENTION_DAYS, boto3_client=boto3_client)
    else:
        handler = RotatingFileHandler(f'{config.LOGDIR}/pgvector_logger.warn', maxBytes=1024*1024, backupCount=5, encoding='utf-8')
    config.APP_LOG_HANDLER = app_log_handler; 
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    pgvector_logger.addHandler(handler)
    config.PGVECTOR_LOGGER = pgvector_logger
    return app_log_handler