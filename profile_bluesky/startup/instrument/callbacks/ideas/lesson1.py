
"""
lesson 1 : example callback
"""

from ...session_logs import logger
logger.info(__file__)

__all__ = [
    'myCallbackBrief', 
    'myCallback',
    ]


def myCallbackBrief(key, doc):
    logger.info(key, len(doc))


def myCallback(key, doc):
    logger.info(key, len(doc))
    for k, v in doc.items():
        print("\t", k, v)
    logger.info("~~~~~~~~~~~~~~~~~~~~")
