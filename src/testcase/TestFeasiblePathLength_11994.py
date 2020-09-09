
import time
from parameterized import parameterized
from src.core.BaseTest import *
from src.field.Elements import Elements
import allure
import pytest
from src.core.getImage import getImage
from src.utils.loggers import JFMlogging

class TestFeasiblePathLength_11994(BaseTest):
    global listInfor
    listInfor = {"testCase2":["login"]}
    def setup_method(self):
        BaseTest.new(self, listInfor)
        global driver,dt
        driver, dt = BaseTest.setUp(self)
        self.logger.info("开始运行测试")
    def teardown_method(self):
        BaseTest.beforeEnd(self)
        driver.quit()
        self.logger.info("测试结束")

    @allure.story("流程2")
    @allure.feature("")
    @allure.description("")
    @getImage
    def testCase2(self): 
        # 1. 首页面 --- click ---> loginname----->login 
        #click -->loginName
        dt.sleep(2)
        #dt.click(self.elements.vd203b1_by, self.elements.vd203b1)
        dt.findView("TEXT","首页")
        #dt.assertDtEquals("TEXT","首页","首页")
        dt.refreshStep()

