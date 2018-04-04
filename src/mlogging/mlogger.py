'''
Created on 20 Mar 2017

@author: 
'''
import os
import json
import logging.config

from filehandler import MFileHandler
from iohandling import get_abs_path

CUR_DIR = os.path.dirname(os.path.realpath(__file__))

class Singleton(type):
    _instances = {}
    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]


#Python2
class MLogger():
    __metaclass__ = Singleton
    '''
    The MagorLogger is a mlogging facilities of the Magor system.
    It helps manage the log messages in a manner that we can store and retrieve it easily.
    
    This class is implementing the Singleton pattern. 
    '''
    @staticmethod
    def setup_logging(
        default_path='./logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'
    ):
        """Setup mlogging configuration
        """
        sys_log_dir = os.path.join(get_abs_path('base_dir'), 'mlogging')
        path = os.path.abspath(os.path.join(sys_log_dir, default_path))
        
        value = os.getenv(env_key, None)
        if value:
            path = value
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
        else:
            #print 'Default level'
            logging.basicConfig(level=default_level)

    @staticmethod
    def get_mlogger(loggername='webhook'):
        MLogger.setup_logging()
        retLogger = logging.getLogger(loggername)
        
        if not retLogger.handlers:
            # Create the new log for each sub-process, like raw, resample, diarize, transcript
            sys_log_dir = os.path.join(get_abs_path('base_dir'), '../logs')
            moduleLoggerPath = os.path.join(sys_log_dir, loggername)
            
            if not os.path.exists(moduleLoggerPath):
                os.makedirs(moduleLoggerPath)
                
            # Set the output file log for each  module logger 
            module_handler = MFileHandler(moduleLoggerPath , retLogger, logging.FileHandler)
            # Set the mlogging level of each module
            module_handler.setLevel(logging.DEBUG)
            # Set the formatter of each module
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
            module_handler.setFormatter(formatter)
            retLogger.addHandler(module_handler)
        return retLogger


def logger(loggername='webhook'):
        return MLogger.get_mlogger(loggername)

