import os
import datetime

# To record the mlogging in process logger
class MFileHandler(object):
    '''
    This class is to customize the FileHandler - to create the file name on the fly
    The output will be the <module>_<date>_<time>.log in the requested dir > logs > 
    '''
    def __init__(self, inDir, logger, handlerFactory, **kw):
        now=datetime.datetime.today().strftime('%Y%m%d')
        #now=datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
        filename='%s_%s.log' % (logger.name.replace(' ','_'), now)
         
        log_folder = os.path.abspath(inDir)
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        kw['filename'] = os.path.join(log_folder, filename)
        self._handler = handlerFactory(**kw)
        

    def __getattr__(self, n):
        if hasattr(self._handler, n):
            return getattr(self._handler, n)
        raise AttributeError, n
