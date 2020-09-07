# _*_ coding:utf-8 _*_
from functools import wraps
from src.core.DT import DT
from src.utils.loggers import JFMlogging
logger = JFMlogging().getloger()


def getImage(function):
    @wraps(function)
    def get_ErrImage(self, *args, **kwargs):
        
        try:
            result = function(self, *args, **kwargs)
        except Exception as e:
            
            logger.info(" %s 脚本运行失败" %(function.__name__))
            self.dt.saveScreenshotPNG1(name="failed  screenshot", pictName="failed  screenshot")
            raise e
        else:
            logger.info(" %s 脚本运行正常" %(function.__name__))
            self.dt.saveScreenshotPNG1(name="pass  screenshot", pictName="passed  screenshot")
    return get_ErrImage