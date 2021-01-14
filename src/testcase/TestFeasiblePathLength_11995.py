
import time
from parameterized import parameterized
from src.core.BaseTest import *
from src.field.Elements import Elements
import allure
import pytest
from src.core.getImage import getImage
from src.utils.loggers import JFMlogging

# class TestFeasiblePathLength_11995(BaseTest):
#     global listInfor
#     listInfor = {"testCase2_2":["login"],"testCase3_2":["wealth"]}
#     def setup_method(self):
#         BaseTest.new(self, listInfor)
#         global driver,dt
#         driver, dt = BaseTest.setUp(self)
#         self.logger.info("开始运行测试")
#     def teardown_method(self):
#         BaseTest.beforeEnd(self)
#         driver.quit()
#         self.logger.info("测试结束")
#
#     @allure.story("流程2")
#     @allure.feature("")
#     @allure.description("")
#     @getImage
#     def testCase2_2(self):
#         # 1. 首页面 --- click ---> loginname----->login
#         #click -->loginName
#         # dt.sleep(2)
#         # dt.click(self.elements.wealth_by, self.elements.wealth_location)
#         #
#         # dt.sleep(2)
#         # dt.click(self.elements.benefit_by, self.elements.benefit_location)
#         #
#         dt.sleep(2)
#         dt.click(self.elements.mytab_by, self.elements.mytab_location)
#         #
#         # dt.sleep(2)
#         # dt.click(self.elements.homepage_by, self.elements.homepage_location)
#         #
#         # dt.sleep(2)
#         # dt.findView("TEXT", "首页")
#         # dt.findView("TEXT", "财富")
#         # dt.findView("TEXT", "优惠")
#         # dt.findView("TEXT", "我的")
#
#         #dt.findView("TEXT", "扫一扫")
#
#         dt.findViewForass("TEXT","首页")
#         dt.refreshStep()
#
#     @allure.story("流程3")
#     @allure.feature("")
#     @allure.description("")
#     @getImage
#     def testCase3_2(self):
#         # 1. 首页面 --- click ---> loginname----->login
#         #click -->wealth
#         dt.sleep(2)
#         dt.click(self.elements.wealth_by, self.elements.wealth_location)
#
#         dt.refreshStep()