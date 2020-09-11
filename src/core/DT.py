import re
import subprocess
import time
import uuid

import cv2
import random
import allure
import pymysql
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import TimeoutException
from skimage.measure import compare_ssim
import platform
import numpy as np
from PIL import Image
from selenium.webdriver.support.wait import WebDriverWait
from configparser import ConfigParser
from src.utils import PicUtil
from src.utils.loggers import JFMlogging

logger = JFMlogging().getloger()
from appium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from appium.webdriver.connectiontype import ConnectionType
from src.core.BaseTest import *
import os, sys, shutil

import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
Pic_Base_Dir = os.path.join(BASE_DIR, 'Screenshot')
currentPath = os.path.dirname(os.path.abspath(__file__))
root_path1 = os.path.abspath(os.path.join(currentPath, "../.."))
config_data = os.path.join(root_path1, 'config.properties')
conf = ConfigParser()
conf.read(config_data)
num_tsv = 0.8
screenshot_p = 0
tsv = conf.get("SectionDb", "thresholdvalue")
screenshot = conf.get("SectionDb", "screenshotCondition")
serail = os.getenv("serial")
if screenshot == "screenshotWhenAssert" or screenshot == "":
    pass
else:
    screenshot_p = int(screenshot)

if tsv == "imageThreshold" or tsv == "":
    pass
else:
    num_tsv = float(tsv) / 100


class DT(object):
    waitTime = 5
    if conf.get("SectionA", "wTime") != "":
        waitTime = int(conf.get("SectionA", "wTime"))

    def __init__(self, driver, m):
        self.driver = driver
        self.liss = 0
        self.base = m
        self.listname = self.base.listEnd
        self.nummm = 0

    def findWebView(self, webview):
        driver = self.driver
        if not webview is None:
            return driver.find_element_by_xpath(webview)
        return None

    def find_element(self, *loc):
        return self.driver.find_element(*loc)

    def refreshStep(self):
        global listname, liss
        if len(self.listname) - 1 == self.liss:
            pass
        else:
            self.liss += 1
            self.nummm = 0

    def clickKeyboard(self, key1):
        if int(key1) == 1:
            logger.info('点击搜索按键')
            time.sleep(0.5)
            self.driver.press_keycode(66)
        elif int(key1) == 2:
            logger.info('点击确定按键')
            time.sleep(0.5)
            self.driver.press_keycode(23)
        else:
            logger.info('操作指令暂无key={0}'.format(key1))

    def getRandomTextFromList(self, p):
        list1 = p.split(",")
        result = random.sample(list1, 1)
        return result[0]

    def getTimeStamp(self):
        self.nummm += 1
        try:
            ts = time.time()
            r = int(round(ts * 1000))
            logger.info("获取当前时间戳成功")
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "getTimeStamp" + str(self.nummm))
            return r

        except Exception as e:
            logger.info("获取时间戳失败")
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "getTimeStamp" + " " + str(self.nummm))
            raise AssertionError(e)

    def getUUID(self, count):
        self.nummm += 1
        try:
            if count < 0:
                logger.info("uuid长度不能小于0")
                self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "getUUID" + " " + str(self.nummm))
                raise AssertionError("createUUID失败")
            r = uuid.uuid4()
            logger.info("生成uuid成功")
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "getUUID" + str(self.nummm))
            return str(r)[0:count]
        except Exception as e:
            logger.info("生成uuid失败")
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "getUUID" + " " + str(self.nummm))
            raise AssertionError(e)

    def getRandomMobile(self):
        logger.info("生成随机手机号成功")
        return self.mobile()

    def getRandomNum(self, text):
        self.nummm += 1
        try:
            an = re.search('^{[#]range*', text)
            if text == "{#mobile}":
                text = self.mobile()
                print("mobile:" + text)
            if an:
                text = self.radom_num(text)
            logger.info("生成随机数成功")
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "createRandomNum" + str(self.nummm))
            return text
        except Exception as e:
            logger.info("生成随机数失败")
            self.saveScreenshotPNG1(
                "Error:" + self.listname[self.liss] + " " + "createRandomNum" + " " + str(self.nummm))
            raise AssertionError(e)

    def combineText(self, expression, *params):
        self.nummm += 1
        try:
            ee = str(expression) + ".format(*params)"
            p = eval(ee)
            logger.info("组合文本成功")
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "combineText" + str(self.nummm))
            return str(p)
        except Exception as e:
            logger.info("组合文本失败")
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "combineText" + " " + str(self.nummm))
            raise AssertionError(e)

    def inputText(self, way, value, text):
        self.nummm += 1
        an = re.search('^({#range)', text)
        if text == "{#mobile}":
            text = self.mobile()
            print("mobile:" + text)
        if an:
            text = str(self.radom_num(text))
            print("随机：" + str(text))
        try:
            if way == 'IMAGE':
                self.findView(way, value)
                self.inputtext(text)
            elif way == "DOUBLE_IMAGE":
                self.findView(way, value)
                self.inputtext(text)
            else:
                self.findView(way, value).clear()
                self.findView(way, value).send_keys(text)
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "inputText" + " " + str(self.nummm))
            logger.info("通过" + way + "方式定位到元素：" + value + "输入值：" + text)
        except TimeoutException as timee:
            logger.info("通过" + way + "方式定位元素：" + value + "超时")
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "inputText" + " " + str(self.nummm))
            raise AssertionError("通过" + way + "方式定位元素：" + value + "超时")
            # raise timee
        except Exception as e:
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "inputText" + " " + str(self.nummm))
            logger.info("未通过" + way + "方式定位到元素：" + value + "输入值：" + text)
            raise AssertionError("未通过" + way + "方式定位到元素：" + value + "输入值：" + text)

    def mobile(self):

        pefixlist = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139", "147", "150", "151",
                     "152", "153", "155", "156", "157", "158", "159", "186", "187", "188"]

        return random.choice(pefixlist) + "".join(random.choice("0123456789") for i in range(8))

    def radom_num(self, text):
        pass
        text = text.replace("{", "")
        text = text.replace("}", "")
        a = text.split("_")
        b = random.randint(int(a[1]), int(a[2]))
        return b

    def click(self, way, value):
        self.nummm += 1
        try:
            if way == 'IMAGE':
                self.findView(way, value)
            elif way == "DOUBLE_IMAGE":
                self.findView(way, value)
            else:
                element = self.findView(way, value)
                if (way != "XY"):
                    element.click()
                else:
                    TouchAction(self.driver).tap(x=element[0], y=element[1]).perform()
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "click" + " " + str(self.nummm))
            logger.info("通过" + way + "方式定位到元素：" + value + "点击")
        except Exception as e:
            logger.info("未通过" + way + "方式定位到元素：" + value + "点击")
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "click" + " " + str(self.nummm))
            raise AssertionError("通过" + way + "方式定位元素：" + value + "超时")

    def get_title(self):
        return self.driver.title

        # 获取某个属性值0520

    def get_attribute(self, way, value, attribute):
        return self.findView(way, value).get_attribute(attribute)

    def saveScreenshotPNG(self, path=Pic_Base_Dir):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 日期
        riqi = time.strftime("%Y-%m-%d", time.localtime())
        pic_dir_path = os.path.join(path, riqi)
        isExists = os.path.exists(pic_dir_path)
        if not isExists:
            os.makedirs(pic_dir_path)
            print(pic_dir_path + "创建成功")
        else:
            print("目录已存在")

        date = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
        filepath = os.path.join(pic_dir_path, date + ".png")
        # screen =self.driver.save_screenshot(pic_dir_path+"/"+date+".png")
        self.driver.get_screenshot_as_file(filepath)
        with allure.step('screenshots'):
            allure.attach.file(filepath, attachment_type=allure.attachment_type.PNG)
        return filepath

    def saveScreenshotPNG1(self, name, pictName="None", path=Pic_Base_Dir):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 日期
        riqi = time.strftime("%Y-%m-%d", time.localtime())
        pic_dir_path = os.path.join(path, riqi)
        isExists = os.path.exists(pic_dir_path)
        if not isExists:
            os.makedirs(pic_dir_path)
            print(pic_dir_path + "创建成功")
        else:
            print("目录已存在")

        date = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
        filepath = os.path.join(pic_dir_path, date + ".png")
        outpath = os.path.join(pic_dir_path, date + "yasuo.png")
        # screen =self.driver.save_screenshot(pic_dir_path+"/"+date+".png")
        self.driver.get_screenshot_as_file(filepath)
        PicUtil.resize_image(filepath, outpath)
        if pictName != "None":
            with allure.step(name):
                allure.attach.file(outpath, name=pictName, attachment_type=allure.attachment_type.PNG)
        else:
            with allure.step(name):
                allure.attach.file(outpath, attachment_type=allure.attachment_type.PNG)
        return filepath

    def saveScreenshotPNG_F(self, path=Pic_Base_Dir):
        # 去除首位空格
        path = path.strip()
        # 去除尾部 \ 符号
        path = path.rstrip("\\")
        # 日期
        riqi = time.strftime("%Y-%m-%d", time.localtime())
        pic_dir_path = os.path.join(path, riqi)
        isExists = os.path.exists(pic_dir_path)
        if not isExists:
            os.makedirs(pic_dir_path)
            print(pic_dir_path + "创建成功")
        else:
            print("目录已存在")

        date = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
        filepath = os.path.join(pic_dir_path, date + ".png")
        # screen =self.driver.save_screenshot(pic_dir_path+"/"+date+".png")
        self.driver.get_screenshot_as_file(filepath)
        return filepath

    def clickWithscreenshot(self, way, value):
        '''
          点击带截图
        '''
        self.nummm += 1
        try:
            self.click(way, value)
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "clickWithscreenshot" + " " + str(self.nummm))
        except:
            logger.info("通过" + way + "方式定位元素：" + value + "超时")
            self.saveScreenshotPNG1(
                "Error:" + self.listname[self.liss] + " " + "clickWithscreenshot" + " " + str(self.nummm))
            raise AssertionError("通过" + way + "方式定位元素：" + value + "超时")

    def XPATH_MAKE(self, text):
        if (text == ""):
            return
        long = len(text)
        lis_text = []
        for i in text:
            lis_text.append(i)
        lis_text = tuple(lis_text)
        all_test = ("[contains(text(),\"%s\")]" * long) % lis_text
        end_test = "//*" + all_test
        return end_test

    def findViewfortime(self, way, value):
        driver = self.driver
        if (way == "ID"):
            element = driver.find_element(by=By.ID, value=value)
        elif (way == "NAME"):
            element = driver.find_element(by=By.NAME, value=value)
        elif (way == "CLASS_NAME"):
            value1 = value.split(":")
            viewList = driver.find_elements(by=By.CLASS_NAME, value=value1[0])
            element = viewList[value1[1]]
        elif (way == "XPATH"):
            element = driver.find_element(by=By.XPATH, value=value)
        elif (way == "CSS_SELECTOR"):
            element = driver.find_element(by=By.CSS_SELECTOR, value=value)
        elif (way == "PARTIAL_LINK_TEXT"):
            element = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=value)
        elif (way == "TAG_NAME"):
            element = driver.find_element(by=By.TAG_NAME, value=value)
        elif (way == "LINK_TEXT"):
            element = driver.find_element(by=By.LINK_TEXT, value=value)
        elif (way == "DYNAMIC_XPATH"):
            value_end = self.XPATH_MAKE(value)
            element = driver.find_element(by=By.XPATH, value=value_end)
        else:
            logger.info("无效的定位方式")
            return False
        return element

    def parseXY(self, value):
        value1 = value.split(",")
        screen_width = int(self.driver.get_window_size()['width'])
        screen_height = int(self.driver.get_window_size()['height'])
        if type(eval(value1[0])) == int:
            xp = int(value1[0])
            yp = int(value1[1])
            if xp > screen_width or yp > screen_height:
                logger.info("参数错误,超出屏幕边界")
                raise AssertionError("参数错误，参数错误,超出屏幕边界")
        else:
            xp = float(value1[0])
            yp = float(value1[1])
            if xp < 0 or xp > 1 or yp < 0 or yp > 1:
                logger.info("参数错误")
                raise AssertionError("参数错误")
            xp = int(xp * screen_width + 0.5)
            yp = int(yp * screen_height + 0.5)
        return int(xp), int(yp)

    def findView(self, way, value):
        driver = self.driver
        max_time = time.time() + 10
        element = None
        while time.time() < max_time:
            try:
                if (way == "ID"):
                    element = driver.find_element(by=By.ID, value=value)
                elif (way == "NAME"):
                    element = driver.find_element(by=By.NAME, value=value)
                elif (way == "TEXT"):
                    element = driver.find_element(by=By.TEXT, value=value)
                elif (way == "CLASS_NAME"):
                    value1 = value.split(":")
                    viewList = driver.find_elements(by=By.CLASS_NAME, value=value1[0])
                    element = viewList[value1[1]]
                elif (way == "XPATH"):
                    element = driver.find_element(by=By.XPATH, value=value)
                elif (way == "CSS_SELECTOR"):
                    element = driver.find_element(by=By.CSS_SELECTOR, value=value)
                elif (way == "PARTIAL_LINK_TEXT"):
                    element = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=value)
                elif (way == "XY"):
                    return self.parseXY(value)
                elif (way == "DYNAMIC_XPATH"):
                    value_end = self.XPATH_MAKE(value)
                    element = driver.find_element(by=By.XPATH, value=value_end)
                elif (way == "IMAGE"):
                    element = self.click_by_image(value)
                elif (way == "DOUBLE_IMAGE"):
                    a = value.split(",")
                    element = self.click_by_2image(a[0], a[1])
                else:
                    print("无效的定位方式")
                    return False
                return element
            except Exception as e:
                pass
        return element

    def findViewForass(self, way, value):

        driver = self.driver
        try:
            if (way == "ID"):
                return WebDriverWait(self.driver, 30).until(lambda driver: driver.find_element(by=By.ID, value=value))
            elif (way == "NAME"):
                return driver.find_element_by_android_uiautomator('new UiSelector().text(\"' + value + '\")')
            elif (way == "TEXT"):
                return WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.find_element(by=By.TEXT, value=value))
            elif (way == "CLASS_NAME"):
                value1 = value.split(":")
                viewList = WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.find_elements(by=By.CLASS_NAME, value=value1[0]))
                return viewList[value1[1]]
            elif (way == "XPATH"):
                return WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.find_element(by=By.XPATH, value=value))
            elif (way == "CSS_SELECTOR"):
                return WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.find_element(by=By.CSS_SELECTOR, value=value))
            elif (way == "PARTIAL_LINK_TEXT"):
                return WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.find_element(by=By.PARTIAL_LINK_TEXT, value=value))
            elif (way == "XY"):
                value1 = value.split(",")
                action = TouchAction(driver)
                action.tap(x=value1[0], y=value1[1]).release().perform()
            elif (way == "DYNAMIC_XPATH"):
                value_end = self.XPATH_MAKE(value)
                return WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.find_element(by=By.XPATH, value=value_end))
            a = 1
            return a
        except:
            a = 0
            return a

    def assertValueIncrease(self, way, value_1, value_2, value):
        self.nummm += 1
        self.sleep(4)
        A = self.findView(way, value_1).text
        B = value_2
        a = self.num_ass(A)
        b = self.num_ass(B)
        if (b + value == a):
            logger.info("参数:" + value_2 + "增加：" + str(value) + "得到：" + A + ",断言成功！")
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "assertValueIncrease" + " " + str(self.nummm))
        else:
            logger.info("参数:" + value_2 + "增加：" + str(value) + "得到：" + A + ",断言失败！")
            self.saveScreenshotPNG1(
                "Error:" + self.listname[self.liss] + " " + "assertValueIncrease" + " " + str(self.nummm))
            raise AssertionError("参数:" + value_2 + "增加：" + str(value) + "得到：" + A + ",断言失败！")

    def swipeElement(self, way, value, direction):
        self.nummm += 1
        try:
            screen_width = self.driver.get_window_size()['width']
            screen_height = self.driver.get_window_size()['height']
            a = self.xy(way, value)
            x = a[0]
            y = a[1]
            if (direction == 'down'):
                h = screen_height / 6
                self.driver.swipe(x, y, x, y + h)
            elif (direction == 'up'):
                h = screen_height / 6
                self.driver.swipe(x, y, x, y - h)
            elif (direction == 'left'):
                w = screen_width / 6
                self.driver.swipe(x, y, x - w, y)
            elif (direction == 'right'):
                w = screen_width / 6
                self.driver.swipe(x, y, x + w, y)
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "swipeElement" + " " + str(self.nummm))
        except:
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "swipeElement" + " " + str(self.nummm))
            raise AssertionError("方向：" + direction + "滑动失败！")

    def num_ass(self, text):
        a = len(text)
        if a <= 3:
            num = int(text)
            return num
        else:
            num = text.replace(",", "")
            num = int(num)
            return num

    # def getValue(self,way,value):
    #     try:
    #         a = self.findView(way, value).text
    #         logger.info("通过" + way + "方式定位到元素：" + value)
    #         self.saveScreenshotPNG1(listname + " " + "getValue" + " " + str(nummm))
    #         return a
    #     except:
    #         self.saveScreenshotPNG1("Error:" + listname + " " + "getValue" + " " + str(nummm))
    #         raise AssertionError("通过" + way + "方式定位元素：" + value + "超时")
    #
    # def assertDtEquals(self,way,value,expect):
    #     '''
    #       断言实际值等于期望值
    #     '''
    #     actual=self.findView(way,value).text
    #     try:
    #         assert (actual == expect)
    #     except Exception as e:
    #         logger.info("实际值：" + actual + "；" + "期望值：" + expect)
    #         raise AssertionError("实际值：" + actual + "；" + "期望值：" + expect)
    def addDataAction(self, value, params, returnType):
        try:
            dict = json.loads(params)
            if "t" not in dict.keys():
                return 'Error 缺少关键字t'
            elif "f" not in dict.keys():
                return 'Error 缺少关键字f'
            type = dict['t']  # 数据类型
            fun = dict['f']  # 数据方法
            if "p" in dict.keys():
                p = dict['p']  # 数据方法参数
                paramLists = p.split(',')
            else:
                paramLists = [""]
            if type == '0':
                '''字符串'''
                if fun == 's':
                    '''拆分'''
                    st = (str(value).split(paramLists[0]))[paramLists[1]]
                    if returnType == 1:
                        return float(st[0])
                    else:
                        return st[0]
                elif fun == 'c':
                    '''切片'''
                    if len(paramLists) == 3:
                        if paramLists[0] == '':
                            return value[:paramLists[1]:paramLists[2]]
                        elif paramLists[1] == '':
                            return value[paramLists[0]::paramLists[2]]
                        elif paramLists[2] == '':
                            return value[paramLists[0]:paramLists[1]:]
                        else:
                            return value[paramLists[0]:paramLists[1]:paramLists[2]]
                    elif len(paramLists) == 2:
                        if paramLists[0] == '':
                            return value[:paramLists[1]:]
                        else:
                            return value[paramLists[0]::]
                    elif len(paramLists) == 0:
                        return value
                    else:
                        return "Error字符串切片请求参数过多"
                else:
                    return 'Error字符串未支持的方法'
            elif type == '1':
                '''字典'''
                if fun == 'k':
                    '''根据K取值'''
                    dict = eval(value)
                    if returnType == 1:
                        return float(dict[paramLists[0]])
                    else:
                        return dict[paramLists[0]]
                else:
                    return 'Error字典未支持的方法'
            elif type == '2':
                '''列表'''
                temp = list(value)
                if fun == 'e':
                    '''遍历列表'''
                    r = ""
                    for t in temp:
                        r += t + ','
                    return r
                elif fun == 'i':
                    '''索引取值'''
                    id = paramLists[0]
                    if id >= len(temp):
                        return 'Error 索引值超出变量长度'
                    else:
                        if returnType == 1:
                            return float(temp[id])
                        else:
                            return temp[id]
                else:
                    return 'Error列表暂未支持的方法'
            elif type == '':
                return value
            else:
                return 'Error数据类型未支持'
        except Exception as e:
            return e.__doc__

    def getValue(self, way, value, params="", return_type=0):
        self.nummm += 1
        try:
            a = self.findView(way, value).text
            logger.info("通过" + way + "方式定位到元素：" + value + "得到" + a)
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "getValue" + " " + str(self.nummm))
            if str(params) == "" or params is None:
                return a
            else:
                result = self.addDataAction(a, params, return_type)
                logger.info('getValue 数据操作返回结果:{0}'.format(result))
                return result
        except:
            logger.info("通过" + way + "方式定位到元素：" + value + "失败")
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "getValue" + " " + str(self.nummm))
            raise AssertionError("通过" + way + "方式定位到元素：" + value + "失败")

    def is_number(self,s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def compare2values(self,var,value,flag):
        if(self.is_number(var) and self.is_number(value)):
            var = float(var)
            value = float(value)
        if(flag==0):
            try:
                assert var == value
                return True
            except Exception as e:
                logger.info("实际值与期望值不相等")
                return False
        elif(flag==1):
            try:
                assert value != var
                return True
            except Exception as e:
                logger.info("期望值等于实际值")
                return False
        elif(flag == 2):
            try:
                assert str(var) in str(value)
                return True
            except Exception as e:
                logger.info("期望值未包含实际值")
                return False


    def assertDtEqualsDB(self, way, value, sql):
        '''
          断言实际值等于期望值
        '''
        actual = self.findView(way, value).text
        expect = self.mysql_search(sql)
        try:
            assert (actual == expect)
        except Exception as e:
            logger.info("实际值：" + actual + "；" + "期望值：" + expect)
            raise AssertionError("实际值：" + actual + "；" + "期望值：" + expect)

    def assertDtContainDB(self, way, value, sql):
        '''
          断言实际值包含期望值
        '''
        actual = self.findView(way, value).text
        expect = self.mysql_search(sql)
        try:
            assert expect in actual
        except Exception as e:
            logger.info("实际值：" + actual + "；" + "期望值：" + expect)
            raise AssertionError("实际值：" + actual + "；" + "期望值：" + expect)

    def assertDtNotEqualsDB(self, way, value, sql):
        '''
          断言实际值不等于期望值
        '''
        actual = self.findView(way, value).text
        expect = self.mysql_search(sql)
        try:
            assert (actual != expect)
        except Exception as e:
            logger.info("实际值：" + actual + "；" + "期望值：" + expect)
            raise AssertionError("实际值：" + actual + "；" + "期望值：" + expect)

    def assertDtContain(self, way, value, text):
        '''
          断言期望值含有实际值
        '''
        if (way == "XY" or ("IMAGE" in way)):
            logger.info("断言相等失败，不支持" + way + "方式")
            raise AssertionError("断言相等失败，不支持" + way + "方式")
        else:
            if screenshot_p == 1:
                self.saveScreenshotPNG()
            expect = self.findView(way, value).text
            actual = str(text)

            if actual in expect:
                pass
            else:
                logger.info("期望值未包含实际值")
                raise AssertionError("期望值未包含实际值")

    def assertDtEquals(self, way, value, text):
        '''
          断言实际值等于期望值
        '''

        if (way == "XY" or ("IMAGE" in way)):
            logger.info("断言失败，不支持" + way + "方式")
            raise AssertionError("断言失败，不支持" + way + "方式")
        else:
            if screenshot_p == 1:
                self.saveScreenshotPNG()
            expect = self.findView(way, value).text
            actual = str(text)
            try:
                assert expect == actual
            except Exception as e:
                logger.info("实际值：" + actual + "；" + "期望值：" + expect + "不相等")
                raise AssertionError("实际值：" + actual + "；" + "期望值：" + expect + "不相等")

    def assertDtNotEquals(self, way, value, text):
        '''
          断言实际值不等于期望值
        '''
        if (way == "XY" or ("IMAGE" in way)):
            logger.info("断言失败，不支持" + way + "方式")
            raise AssertionError("断言失败，不支持" + way + "方式")
        else:
            if screenshot_p == 1:
                self.saveScreenshotPNG()
            expect = self.findView(way, value).text
            actual = str(text)
            try:
                assert expect != actual
            except Exception as e:
                logger.info("实际值：" + actual + "；" + "期望值：" + expect + "相等")
                raise AssertionError("实际值：" + actual + "；" + "期望值：" + expect + "相等")

    def assertIsSelected(self, way, value):
        '''
          断言期某个值是否被选中0520
        '''
        try:
            assert self.findView(way, value).is_selected()
        except Exception as e:
            raise AssertionError

    def assertIsNotSelected(self, way, value):
        '''
          断言期某个值是否被选中0520
        '''
        try:
            assert self.findView(way, value).is_selected() == False
        except Exception as e:
            raise AssertionError

    def assertIsDisplayed(self, way, value):
        '''
          断言期某个值是否显示0520
        '''
        try:
            assert self.findView(way, value).is_displayed()
            raise AssertionError
        except Exception as e:
            pass

    def assertIsNotDisplayed(self, way, value):
        '''
          断言期某个值是否显示0520
        '''
        try:
            assert self.findView(way, value).is_displayed()
            raise AssertionError
        except Exception as e:
            pass

    def assertIsEnabled(self, way, value):
        '''
          断言期某个值是否可编辑0520
        '''
        try:
            assert self.findView(way, value).is_enabled()
        except Exception as e:
            raise AssertionError

    def assertIsNotEnabled(self, way, value):
        '''
          断言期某个值是否可编辑0520
        '''
        try:
            assert self.findView(way, value).is_enabled() == False
        except Exception as e:
            raise AssertionError

    def assertAttribute(self, way, value, attribute, expect):
        '''
          断言属性值与期望值相同
        '''
        actual = self.get_attribute(way, value, attribute)
        try:
            assert (expect == actual)
        except Exception as e:
            raise AssertionError

    def dbClick(self, way, value):
        '''寻找元素进行双击
           :Args: way:string
           :Args value:string
        '''
        self.nummm += 1
        try:
            if (way == "XY"):
                xp, yp = self.parseXY(value)
                # TouchAction(self.driver).tap(element=None, x=xp, y=yp, count=4).release().perform()
            else:
                action = TouchAction(self.driver)
                element = self.findView(way, value)
                b = element.size
                a = element.location
                x1 = b["width"]
                y1 = b["height"]
                x2 = a["x"]
                y2 = a["y"]
                xp = int(x1 / 2 + x2)
                yp = int(y1 / 2 + y2)
                print("点击坐标为:" + str(xp) + ";" + str(yp))
                # action.tap(None, x=x, y=y, count=4).release().perform()
            # if self.getVerion() < 10:
            #     if self.getVerion() <= 7:
            #         counts = 5
            #     else:
            #         counts = 4
            #     TouchAction(self.driver).tap(x=xp, y=yp, count=counts).release().perform()
            # else:
            #     if str(serail) == "" or serail is None:
            #         command = "adb shell \"input tap {0} {1} && input tap {0} {1}\"".format(xp, yp)
            #     else:
            #         command = "adb -s {0} shell \"input tap {1} {2} && input tap {1} {2}\"s".format(serail,
            #                                                                                         xp, yp)
            #     os.popen(command)
            # self.sleep(2)
            self.__monkey_double_click(x=xp, y=yp)
            logger.info("通过" + way + "方式定位到元素：" + value + "进行双击")
            self.saveScreenshotPNG1("Success:" + self.listname[self.liss] + " " + "dbClick" + " " + str(self.nummm))
        except:
            logger.info("未通过" + way + "方式定位到元素：" + value + "双击")
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "dbClick" + " " + str(self.nummm))
            raise AssertionError("通过" + way + "方式定位元素：" + value + "双击超时")

    def __monkey_double_click(self, x, y):
        text_monkey = "count= 1\nspeed= 1.0\nstart data >>\n" \
                      "DispatchPointer(5109520,5109520,0,{x},{y},0,0,0,0,0,0,0)\n" \
                      "DispatchPointer(5109520,5109520,1,{x},{y},0,0,0,0,0,0,0)\n" \
                      "UserWait(200)\n" \
                      "DispatchPointer(5109520,5109520,0,{x},{y},0,0,0,0,0,0,0)\n" \
                      "DispatchPointer(5109520,5109520,1,{x},{y},0,0,0,0,0,0,0)\n".format(x=x, y=y)
        if str(serail) == "" or serail is None:
            commoncmd = "adb shell "
            commoncmdPush = " adb "
        else:
            commoncmd = "adb -s " + serail + " shell "
            commoncmdPush = " adb -s " + serail
        os.popen(commoncmd + "\"rm -rf /data/local/tmp/monkey.txt\"")
        time.sleep(0.5)
        folder = os.getcwd()
        file = os.path.join(folder, "monkey.txt")
        if os.path.exists(file):
            os.remove(file)

        with open(file, "w+") as f:
            f.write(text_monkey)
        os.popen(commoncmdPush + " push " + file + " /data/local/tmp")
        time.sleep(0.5)
        os.popen(commoncmd + "\"monkey -f /data/local/tmp/monkey.txt 1\"")
        logger.info("执行双击操作命令为：" + commoncmd + "\"monkey -f /data/local/tmp/monkey.txt 1\"")
        time.sleep(0.5)
        os.remove(file)
        print("")

    def longPress(self, way, value):
        '''寻找元素保持点击
                   :Args: way:string
                   :Args value:string
                '''
        self.nummm += 1
        try:
            if (way == "XY"):
                x, y = self.parseXY(value)
                TouchAction(self.driver).long_press(x=x, y=y, duration=5000).release().perform()
            else:
                web_element = self.findView(way, value)
                action = TouchAction(self.driver)
                action.long_press(web_element).perform()
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "longPress" + " " + str(self.nummm))
            logger.info("通过" + way + "方式定位到元素：" + value + "长按")
        except:
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "longPress" + " " + str(self.nummm))
            raise AssertionError("通过" + way + "方式定位元素：" + value + "超时")

    # #fixme 需要左滑动和右滑动的js代码
    # def swipe(self,way="UP"):
    #     '''web页面滑动，
    #        :Args: UP:滑动到最底部
    #        :Args DOWN:滑动到最上部
    #     '''
    #     driver = self.driver
    #     try:
    #         if(way is "UP"):
    #             js="window.scrollTo(0,document.body.scrollHeight)"
    #             driver.execute_script(js)
    #         elif(way is "DOWN"):
    #             js = "window.scrollTo(0,0)"
    #             driver.execute_script(js)

    #     except Exception as e:
    #         raise e
    def swipe(self, direction):
        self.nummm += 1
        try:
            screen_width = self.driver.get_window_size()['width']
            screen_height = self.driver.get_window_size()['height']
            if (direction == 'down'):
                self.driver.swipe(screen_width / 2, screen_height / 4, screen_width / 2, screen_height * 3 / 4)
            elif (direction == 'up'):
                self.driver.swipe(screen_width / 2, screen_height * 3 / 4, screen_width / 2, screen_height / 4)
            elif (direction == 'left'):
                self.driver.swipe(screen_width * 5 / 6, screen_height / 2, screen_width / 6, screen_height / 2)
            elif (direction == 'right'):
                self.driver.swipe(screen_width / 6, screen_height / 2, screen_width * 5 / 6, screen_height / 2)
            else:
                print("无效的方向")

            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "swipe" + " " + str(self.nummm))
        except:
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "swipe" + " " + str(self.nummm))
            raise AssertionError("通过" + direction + "方向滑动失败")

    def drag_and_drop(self, way, value, way1, value1):
        '''寻找元素进行拖拽
                   :Args: way:string
                   :Args value:string
                '''
        web_element_source = self.findView(way, value)  # 源元素
        web_element_target = self.findView(way1, value1)  # 目标元素
        ActionChains(self.driver).drag_and_drop(web_element_source, web_element_target).perform()

    def sleep(self, second):
        time.sleep(second)

    # fixme 切换回主窗口时需要增加一个方法
    def frame(self, name):
        # driver定位至frame/iframe
        driver = self.driver
        driver.switch_to_frame(name)
        # driver.switch_to.default_content()   切换回主窗口

    def frameByElement(self, way, value):
        driver = self.driver
        frame = self.findView(way, value)
        driver.switch_to_frame(frame)
        # driver.switch_to.default_content()   切换回主窗口

    def window(self):
        # driver当前页面的所有句柄，默认切换到最后一个
        handles = self.driver.window_handles
        self.driver.switch_to_window(handles[-1])

    def close(self):
        # driver关闭当前页面
        self.driver.close()

    def connectDb(self):
        '''连接数据库'''
        try:
            # 连接数据库
            self.conn = pymysql.connect(host=conf.get('SectionDb', 'host'),
                                        user=conf.get('SectionDb', 'username'),
                                        password=conf.get('SectionDb', 'password'),
                                        db=conf.get('SectionDb', 'database'),
                                        port=int(conf.get('SectionDb', 'port')),
                                        charset='utf8',
                                        cursorclass=pymysql.cursors.DictCursor)
            # 通过cursor创建游标
            self.cur = self.conn.cursor()
        except Exception as e:
            logger.error("连接数据库错误")
            raise AssertionError("连接数据库错误")

    def mysql_search(self, sql):
        '''查询数据'''
        try:
            self.connectDb()
            self.cur.execute(sql)
            result = self.cur.fetchone()  # 查询数据库单条数据
            if (len(result) >= 1):
                res = str(list(result.values())[0])
            else:
                logger.error("未查询到数据")
            # res = re.match('','')
            # result = cursor.fetchall() #查询数据库多条数据
            # 提交sql
            self.conn.commit()
            self.conn.close()
            return res
        except Exception as e:
            self.conn.close()
            logger.error("查询错误")
            raise AssertionError("查询错误")

    def switchContext(self, name):
        '''切换进入webview或者原生'''
        contexts = self.driver.contexts
        for i in contexts:
            if (contexts.index(i) == name):
                self.driver.switch_to.context(contexts[i])
                currentContext = self.driver.context
                if (currentContext == name):
                    logger.info("切换到context：" + name)
                else:
                    logger.info("未切换到context：" + name)
            else:
                logger.info("不存在的context：" + name)

    def Region_picture_assertion_double(self, template_jpg_1, template_jpg_2):
        sysstr = platform.system()
        if screenshot_p == 1:
            self.saveScreenshotPNG_F()

        wa = self.scrpath()
        la = self.saveScreenshotPNG_F()
        template_jpg = wa[1] + template_jpg_1
        template_jpg_5 = wa[1] + template_jpg_2

        x1, y1, x2, y2 = self.find_pict_l(la, template_jpg)
        if y1 == '0':
            if y1 == '0' and x2 == '0':
                kk = 0
                return kk
                # print('未匹配相应元素，操作系统原因！')
                # logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + template_jpg_1 + "，断言失败，操作系统原因")
                # raise AssertError("非windows系统或者Linux系统")
            # print('未匹配相应元素')
            # logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + template_jpg_1 + "，断言失败")
            # raise AssertError("图片断言未找到相应元素")

        else:
            self.get_image(x1, y1, x2, y2, la, wa[2])
            x1, y1, x2, y2 = self.find_pict_l(wa[2], template_jpg_5)

            if y2 == '0':
                kk = 0
                return kk
                # print('未匹配相应元素')
                # logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + template_jpg_2 + "，断言失败")
                # raise AssertError("图片断言未找到相应元素")

            # logger.info("通过" + 'IMAGE' + "方式定位到元素：" + template_jpg_2 + "，断言成功")
            kk = 1
            return kk

    def logDelay(self, way, value, name):
        self.nummm += 1
        starttime = time.time()
        max_time = time.time() + 30
        totalTime = None
        while time.time() < max_time:

            try:
                self.findViewfortime(way, value)
                totalTime = time.time() - starttime
                str_time = time.time()
                str_time = str(int(round(str_time * 1000)))
                self.base.f += name + " " + str(totalTime)[0:6] + " s " + str_time + " 0" + "\n"
                self.saveScreenshotPNG1(
                    self.listname[self.liss] + " " + "logDelay" + " " + "步骤" + str(self.nummm) + "业务用时：" + str(
                        totalTime)[0:6])
                break
            except:
                totalTime = time.time() - starttime
        totalTime = time.time() - starttime
        if totalTime >= 30:
            str_time = time.time()
            str_time = str(int(round(str_time * 1000)))
            self.base.f += name + " 0 s " + str_time + " 1" + "\n"
            self.saveScreenshotPNG1(
                "Error:" + self.listname[self.liss] + " " + "logDelay" + " " + "步骤" + str(self.nummm) + "超时预定时间30秒")
            raise AssertionError(
                "Error:" + self.listname[self.liss] + " " + "logDelay" + " " + "步骤" + str(self.nummm) + "超时预定时间30秒")

    def swipeElement(self, way, value, direction):
        screen_width = self.driver.get_window_size()['width']
        screen_height = self.driver.get_window_size()['height']
        a = self.xy(way, value)
        x = a[0]
        y = a[1]
        if (direction == 'down'):
            h = screen_height / 6
            self.driver.swipe(x, y, x, y + h)
        elif (direction == 'up'):
            h = screen_height / 6
            self.driver.swipe(x, y, x, y - h)
        elif (direction == 'left'):
            w = screen_width / 6
            self.driver.swipe(x, y, x - w, y)
        elif (direction == 'right'):
            w = screen_width / 6
            self.driver.swipe(x, y, x + w, y)

    def getRandomTextFromList(self, p):
        list1 = p.split(",")
        result = random.sample(list1, 1)
        return result[0]

    def getTimeStamp(self):
        # self.nummm += 1
        try:
            ts = time.time()
            r = int(round(ts * 1000))
            logger.info("获取当前时间戳成功")
            # self.saveScreenshotPNG1(self.listname[self.liss] + " " + "getTimeStamp" + str(self.nummm))
            return r

        except Exception as e:
            logger.info("获取时间戳失败")
            # self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "getTimeStamp" + " " + str(self.nummm))
            raise AssertionError(e)

    def getUUID(self, count):
        # self.nummm += 1
        try:
            if (count > 32 or count < 0):
                logger.info("uuid长度不能大于32或者小于0")
                # self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "getUUID" + " " + str(self.nummm))
                raise AssertionError("createUUID失败")
            r = uuid.uuid4()
            logger.info("生成uuid成功")
            # self.saveScreenshotPNG1(self.listname[self.liss] + " " + "getUUID" + str(self.nummm))
            return str(r)[0:count]
        except Exception as e:
            logger.info("生成uuid失败")
            # self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "getUUID" + " " + str(self.nummm))
            raise AssertionError(e)

    def getRandomMobile(self):
        logger.info("生成随机手机号成功")
        return self.mobile()

    def getRandomNum(self, value1, value2):
        # self.nummm += 1
        try:
            logger.info("生成随机数成功")
            return random.randint(value1, value2)
            # self.saveScreenshotPNG1(self.listname[self.liss] + " " + "createRandomNum" + str(self.nummm))
        except Exception as e:
            logger.info("生成随机数失败")
            # self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "createRandomNum" + " " + str(self.nummm))
            raise AssertionError(e)

    def combineText(self, expression, *params):
        # self.nummm += 1
        try:
            # ee = str(expression) + ".format(*params)"
            # p = eval(ee)
            p = str(expression).format(*params)
            logger.info("组合文本成功")
            # self.saveScreenshotPNG1(self.listname[self.liss] + " " + "combineText" + str(self.nummm))
            return str(p)
        except Exception as e:
            logger.info("组合文本失败")
            # self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "combineText" + " " + str(self.nummm))
            raise AssertionError(e)

    def xy(self, way, value):

        v = self.findView(way, value)
        b = v.size
        a = v.location
        x1 = b["width"]
        y1 = b["height"]
        x2 = a["x"]
        y2 = a["y"]
        x = x1 / 2 + x2
        y = y1 / 2 + y2
        return x, y

    def execShell(self, text):
        self.nummm += 1
        command = ""
        if str(serail) == "" or serail is None:
            command = "adb " + str(text)
        else:
            command = "adb -s {0} {1}".format(serail, text)
        shellResult = os.popen(command).read()
        logger.info("运行成功，命令：adb" + text)
        self.saveScreenshotPNG1(self.listname[self.liss] + " " + "execShell" + " " + str(self.nummm))
        return shellResult

    def scrpath(self, path=Pic_Base_Dir, a=BASE_DIR):
        path = path.strip()
        path = path.rstrip("/")
        b = a[:-4] + '/images/element/'
        riqi = time.strftime("%Y-%m-%d", time.localtime())
        pic_dir_path = os.path.join(path, riqi)
        isExists = os.path.exists(pic_dir_path)
        # print('pi:' + pic_dir_path)
        if not isExists:
            os.makedirs(pic_dir_path)
            print(pic_dir_path + "创建成功")
        else:
            print("目录已存在")
        date = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
        filepath = os.path.join(pic_dir_path, date + ".png")
        filepath_1 = os.path.join(pic_dir_path, date + "_1" + ".png")
        return filepath, b, filepath_1

    def same_high_pict(self, img, template):
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

        threshold = num_tsv
        loc = np.where(res >= 0.8)

        x = len(loc[0])
        return x

    def get_image(self, left, top, right, bottom, path_1, path_2):

        page_snap_obj = self.get_snap(path_1)
        image_obj = page_snap_obj.crop((left, top, right, bottom))
        image_obj.save(path_2)
        return path_2

    def get_snap(self, path):

        page_snap_obj = Image.open(path)
        return page_snap_obj

    def picture_xy(self, img, template):
        h, w = template.shape[:2]
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        left_top = max_loc
        right_bottom = (left_top[0] + w, left_top[1] + h)

        return (left_top[0], left_top[1], right_bottom[0], right_bottom[1])

    def find_pict_l(self, img_jpg, template_jpg):

        img = cv2.imread(img_jpg, 0)
        template = cv2.imread(template_jpg, 0)

        x = self.same_high_pict(img, template)
        # x = 1
        if x == 0:
            a = ('未匹配相应元素', "0", '0', "0")
        else:
            a = self.picture_xy(img, template)
        return a

    def Region_picture_assertion_alone(self, template_jpg):
        if screenshot_p == 1:
            self.saveScreenshotPNG_F()

        la = self.saveScreenshotPNG_F()
        wa = self.scrpath()
        template_jpg = wa[1] + template_jpg
        x, y, x1, y1 = self.find_pict_l(la, template_jpg)

        if y1 == '0':
            kk = 0
            return kk
            # print('未匹配相应元素')
            # logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + template_jpg + "，断言失败")
            # raise AssertError("图片断言未找到相应元素")

        else:
            kk = 1
            return kk
            # logger.info("通过" + 'IMAGE' + "方式定位到元素：" + template_jpg + "，断言成功")

    def scrpath_i(self, a=BASE_DIR):
        path = a.strip()
        path = path.rstrip("/")
        a = path[:-4] + '/images/node/'
        return a

    def intelligentlyWaitByRegion(self, way, value):
        i = 0
        if way == "IMAGE":
            while True:
                ll = self.Region_picture_assertion_alone(value)
                if ll == 0:
                    self.sleep(2)
                    i += 1
                elif ll == 1:
                    break
                if i == 3:
                    logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + value + "，断言失败")
                    raise AssertionError("智能等待未找到相应元素")

        elif way == "DOUBLE_IMAGE":
            a = value.split(",")
            while True:
                ll = self.Region_picture_assertion_double(a[1], a[0])
                if ll == 0:
                    self.sleep(2)
                    i += 1
                elif ll == 1:
                    break
                if i == 3:
                    logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + a[0] + "，断言失败")
                    raise AssertionError("智能等待未找到相应元素")

    def assertDtVideoStop(self):
        i = 0
        n = 0
        m = 0
        k = 0
        C = []
        A = self.saveScreenshotPNG_F()
        while k < 3:

            self.sleep(3)

            D = self.saveScreenshotPNG_F()

            if m == 0:
                a = self.intelligently(A, D)
            else:
                a = self.intelligently(C[-1], D)
            m += 1
            if a >= 0.9:
                i += 1
            elif a <= 0.5:
                n += 1
            if i == 3:
                logger.info("视频停止或卡住，未能播放成功")
            C.append(D)
            k += 1
            if n == 3:
                logger.info("视频播放成功")
                raise AssertionError("视频断言失败")
        if i != 3:
            logger.info("视频播放成功")
            raise AssertionError("视频断言失败")

    def inputtext(self, text):
        self.nummm += 1
        try:
            self.driver.set_clipboard_text(text)
            self.sleep(3)
            self.driver.press_keycode(50, 4096)
            logger.info("输入" + text)
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "inputtext" + " " + str(self.nummm))
        except:
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "inputtext" + " " + str(self.nummm))
            raise AssertionError("输入" + text)

    def input_text(self, way, value, text):
        self.nummm += 1
        try:
            self.click(way, value)
            self.sleep(3)
            self.driver.set_clipboard_text(text)
            self.sleep(3)
            self.driver.press_keycode(50, 4096)
            logger.info("通过" + way + "方式定位到元素：" + value + "输入")
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "input_text" + " " + str(self.nummm))
        except:
            self.saveScreenshotPNG1("Error:" + self.listname[self.liss] + " " + "input_text" + " " + str(self.nummm))
            raise AssertionError("通过" + way + "方式定位元素：" + value + "超时")

    def isElementExist(self, way, value, timeo='30'):
        '''
          判断元素是否存在
        '''
        try:
            if way == "IMAGE":
                a = self.Region_picture_assertion_alone(value)
                if a == 1:
                    return True
                else:
                    return False
            elif way == "DOUBLE_IMAGE":
                m = value.split(",")
                a = self.Region_picture_assertion_double(m[1], m[0])
                if a == 1:
                    return True
                else:
                    return False
            else:
                a = self.untilTime(way, value, timeo)
                return a


        except Exception as e:
            return False

    def assertElementExist(self, way, value, timeo='30'):
        '''
          判断元素是否存在
        '''
        try:
            if way == "IMAGE":
                a = self.Region_picture_assertion_alone(value)
                if a == 1:
                    pass
                else:
                    raise AssertionError("断言元素" + value + "不存在")
            elif way == "DOUBLE_IMAGE":
                m = value.split(",")
                a = self.Region_picture_assertion_double(m[1], m[0])
                if a == 1:
                    pass
                else:
                    raise AssertionError("断言元素" + value + "不存在")
            else:
                a = self.untilTime(way, value, timeo)
                if a:
                    pass
                else:
                    raise AssertionError("断言元素不存在")
        except Exception as e:
            raise AssertionError("断言失败")

    def waitElementExist(self, way, value, timeo='30'):
        '''
          判断元素是否存在
        '''
        try:
            if way == "IMAGE":
                a = self.Region_picture_assertion_alone(value)
                if a == 1:
                    pass
                else:
                    raise AssertionError("断言元素" + value + "超时")
            elif way == "DOUBLE_IMAGE":
                m = value.split(",")
                a = self.Region_picture_assertion_double(m[1], m[0])
                if a == 1:
                    pass
                else:
                    raise AssertionError("断言元素" + value + "超时")
            else:
                a = self.untilTime(way, value, timeo)
                if a:
                    pass
                else:
                    raise AssertionError("断言元素超时")
        except Exception as e:
            raise e

    def isElementNotExist(self, way, value, timeo='30'):
        '''
          判断元素是否存在
        '''
        try:
            if way == "IMAGE":
                a = self.Region_picture_assertion_alone(value)
                if a == 1:
                    return False
                else:
                    return True
            elif way == "DOUBLE_IMAGE":
                m = value.split(",")
                a = self.Region_picture_assertion_double(m[1], m[0])
                if a == 1:
                    return False
                else:
                    return True
            else:
                a = self.untilTime(way, value, timeo)
                return a
        except Exception as e:
            return True

    def inputAndSearch(self, way, value, text):
        self.nummm += 1
        try:
            self.click(way, value)
            self.sleep(3)
            self.driver.set_clipboard_text(text)
            self.sleep(1)
            self.driver.press_keycode(50, 4096)
            self.sleep(2)
            self.driver.press_keycode(84)
            logger.info("通过" + way + "方式定位到元素：" + value + "输入" + text)
            self.saveScreenshotPNG1(self.listname[self.liss] + " " + "inputAndSearch" + " " + str(self.nummm))
        except:
            self.saveScreenshotPNG1(
                "Error:" + self.listname[self.liss] + " " + "inputAndSearch" + " " + str(self.nummm))
            raise AssertionError("输入" + text + "失败")

    def clickEByXY(self, x, y):
        x = int(x)
        y = int(y)
        x = str(x)
        y = str(y)
        out = os.popen("adb shell input tap %s %s" % (x, y)).read()
        if out == "":
            logger.info("点击成功，坐标为" + x + "," + y)
        else:
            logger.info("点击失败，错误原因：" + out)
            raise AssertionError("点击失败，错误原因：" + out)

    def click_by_image(self, template_jpg):
        try:
            wa = self.scrpath()
            la = self.saveScreenshotPNG_F()
            template_jpg = wa[1] + template_jpg
            x, y = self.find_pict(la, template_jpg)

            if y == '0':
                logger.info("未通过" + "IMAGE" + "方式定位到元素：" + template_jpg)
                raise AssertionError("未通过" + "IMAGE" + "方式定位到元素：" + template_jpg)
            else:
                time.sleep(2)
                x = str(x)
                y = str(y)
                self.clickEByXY(x, y)
                logger.info("通过" + 'IMAGE' + "方式定位到元素：" + template_jpg + "点击")
        except Exception as e:
            logger.info("未通过" + "IMAGE" + "方式定位到元素：" + template_jpg + "点击")
            raise AssertionError("未通过" + "IMAGE" + "方式定位到元素：" + template_jpg + "点击")

    def click_by_2image(self, template_jpg_1, template_jpg_2):

        wa = self.scrpath()
        la = self.saveScreenshotPNG_F()
        template_jpg = wa[1] + template_jpg_1
        template_jpg_5 = wa[1] + template_jpg_2

        x1, y1, x2, y2 = self.find_pict_l(la, template_jpg)

        if y1 == '0':
            if y1 == '0' and x2 == 0:
                print('未匹配相应元素，操作系统原因！')
                logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + template_jpg_1 + "，断言失败，操作系统原因")
                raise AssertionError("非windows系统或者Linux系统")
            print('未匹配相应元素')
            logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + template_jpg_1 + "，断言失败")
            raise AssertionError("未通过" + "IMAGE" + "方式定位到元素：" + template_jpg_2 + "点击")

        else:

            self.get_image(x1, y1, x2, y2, la, wa[2])
            x3, y3, x4, y4 = self.find_pict_l(wa[2], template_jpg_5)

            if y4 == '0':
                print('未匹配相应元素')
                logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + template_jpg_2)
                raise AssertionError("2图片未找到相应元素")
            else:

                self.clickEByXY((2 * int(x1) + int(x3) + int(x4)) / 2, (2 * int(y1) + int(y3) + int(y4)) / 2)
                logger.info("通过" + 'IMAGE' + "方式定位到元素：" + template_jpg_2 + "点击")

    def untilTime(self, text, timeout, timeo='30'):

        if timeo == '30':
            timeout = int(timeout)
            a = self.is_text_present(text, timeout)
            return a
        else:
            timeo = int(timeo)
            a = self.is_ele_present(text, timeout, timeo)
            return a

    def is_text_present(self, text, timeout):
        print("starttime" + str(time.time()))
        max_time = time.time() + timeout
        while time.time() < max_time:
            locator = "//*[contains(@text, \"" + text + "\")]"
            try:
                self.sleep(0.2)
                self.driver.find_element(by=By.XPATH, value=locator).click()
                print("endtime" + str(time.time()))
                return True

            except:
                pass

        return False

    def is_ele_present(self, way, value, timeout):
        print("starttime" + str(time.time()))
        max_time = time.time() + timeout
        i = 0
        while time.time() < max_time:
            try:
                # i+=1
                self.sleep(0.2)
                element = self.findViewfortime(way, value)
                print("endtime" + str(time.time()))
                return True
            except:
                pass
        return False

    def assertDtVideoShown(self):
        i = 0
        n = 0
        m = 0
        C = []
        k = 0
        A = self.saveScreenshotPNG_F()
        while k < 3:

            self.sleep(2)

            D = self.saveScreenshotPNG_F()

            if m == 0:
                a = self.intelligently(A, D)
            else:
                a = self.intelligently(C[-1], D)
            m += 1
            if a >= 0.9:
                i += 1
            elif a <= 0.5:
                n += 1
            if i == 3:
                logger.info("视频停止或卡住，未能播放成功")
                raise AssertionError("视频断言失败")

            C.append(D)
            k += 1
        if i != 3:
            logger.info("视频播放成功")

    def intelligently(self, file1, file2):

        a = self.scrpath_i()

        file_name = file1

        score = self.compare_image(file_name, file2)
        return score

    def assertDtRegionExist(self, way, value):

        if way == "IMAGE":
            while True:
                ll = self.Region_picture_assertion_alone(value)
                if ll == 0:
                    logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + value + "，断言失败")
                    raise AssertionError("单图断言失败，目标图未找到")
                elif ll == 1:
                    logger.info("通过" + 'IMAGE' + "方式定位到元素：" + value + "，断言成功")
                    break

        elif way == "DOUBLE_IMAGE":
            a = value.split(",")
            while True:
                ll = self.Region_picture_assertion_double(a[1], a[0])
                if ll == 0:
                    logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + value + "，断言失败")
                    raise AssertionError("单图断言失败，目标图未找到")
                elif ll == 1:
                    logger.info("通过" + 'IMAGE' + "方式定位到元素：" + value + "，断言成功")
                    break

    def assertDtRegionNotExist(self, way, value):
        if way == "IMAGE":
            while True:
                ll = self.Region_picture_assertion_alone(value)
                if ll == 1:
                    logger.info("通过" + 'IMAGE' + "方式定位到元素：" + value + "，断言失败")
                    raise AssertionError("单图断言失败，目标图已找到")
                elif ll == 0:
                    logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + value + "，断言成功")
                    break

        elif way == "DOUBLE_IMAGE":
            a = value.split(",")
            while True:
                ll = self.Region_picture_assertion_double(a[1], a[0])
                if ll == 1:
                    logger.info("通过" + 'IMAGE' + "方式定位到元素：" + value + "，断言失败")
                    raise AssertionError("单图断言失败，目标图已找到")
                elif ll == 0:
                    logger.info("通过" + 'IMAGE' + "方式未定位到元素：" + value + "，断言成功")
                    break

    def scrpath_l(self, a=BASE_DIR):
        path = a.strip()
        path = path.rstrip("/")
        a = path[:-4] + '/images/element/'
        return a

    def compare_image(self, path_image1, path_image2):

        imageA = cv2.imread(path_image1)
        imageB = cv2.imread(path_image2)

        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

        (score, diff) = compare_ssim(grayA, grayB, full=True)
        print("SSIM: {}".format(score))
        return score

    def find_pict(self, img_jpg, template_jpg):

        img = cv2.imread(img_jpg, 0)
        template = cv2.imread(template_jpg, 0)

        x = self.same_high(img, template)
        if x == 0:
            a = ('未匹配相应元素', '0')
        else:
            a = self.picture_ce(img, template)
        return a

    def same_high(self, img, template):

        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        threshold = num_tsv
        loc = np.where(res >= threshold)

        x = len(loc[0])

        return x

    def picture_ce(self, img, template):
        h, w = template.shape[:2]
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        left_top = max_loc
        right_bottom = (left_top[0] + w, left_top[1] + h)
        click_x = int((right_bottom[0] + left_top[0]) / 2)
        click_y = int((right_bottom[1] + left_top[1]) / 2)

        print('(' + '坐标点为：' + '000' + str(click_x) + str(click_y) + ')')
        return (click_x, click_y)

    def startLogcat(self, tag1, tag2, sysType):

        '''adb  需要修配合修改 各设备'''
        if sysType == "Windows":
            cmd_str = " logcat -d|findstr -s \"{0} {1} MiguSsoServic\"".format(tag1, tag2)
        else:
            if tag2 == "" or tag2 is None:
                com_str = " logcat -d|egrep -e \"{0}|MiguSsoServic\"".format(tag1)
            else:
                cmd_str = " logcat -d|egrep -e \"{0}|{1}|MiguSsoServic\"".format(tag1, tag2)
        self.nummm += 1
        command = ""
        if str(serail) == "" or serail is None:
            command = "adb " + str(cmd_str)
        else:
            command = "adb -s {0} {1}".format(serail, cmd_str)

        logger.info("执行的adb logcat 命令为:" + command)
        strs_obj = os.popen(command)
        result = strs_obj.read()
        logger.info("执行adb logcat 结果为:" + result)
        return result

    def parseTime(self, text):
        '''解析文本日志'''
        regEx = "\d{1,2}:\d{1,2}:\d{1,2}.\d{1,3}"
        mat = re.search(regEx, text)
        s = mat.group(0)
        hours, minutes, seconds = (["0", "0"] + s.split(":"))[-3:]
        hours = int(hours)
        minutes = int(minutes)
        seconds = float(seconds)
        miliseconds = int(3600000 * hours + 60000 * minutes + 1000 * seconds)
        return miliseconds

    def logVideoDelayTime(self, way, value, type="APP", name="logDelay"):
        '''视频延时方法'''
        sysstr = platform.system()
        tag1 = "MediaFocusControl"
        tag2 = "IJKMEDIA"
        if str(type).lower() == "play":
            self.execShell("logcat -c")
            self.click(way, value)
        elif str(type).lower() == "h5":
            tag2 = ""
        self.sleep(5)
        result = self.startLogcat(tag1, tag2, sysstr)
        resultLines = result.split('\n')
        resultLines = [line for line in resultLines if line != '']  # 去除拆分列表的空行
        if len(resultLines) > 1:
            bengin = self.parseTime(resultLines[0])
            end = self.parseTime(resultLines[len(resultLines) - 1])
            if str(type).lower() == "h5":
                for l in resultLines:
                    if str(l).__contains__("requestAudioFocus()"):
                        end = self.parseTime(l)
                        break

            delyTime = (end - bengin) / 1000.0
            str_time = time.time()
            str_time = str(int(round(str_time * 1000)))
            self.base.f += name + " " + str(delyTime) + " s " + str_time + "\n"
            self.saveScreenshotPNG1(
                self.listname[self.liss] + " " + "logVideoDelayTime" + ":" + str(
                    delyTime))
        else:
            self.base.f += name + " 0 s 0 1" + "\n"
            logger.info("adb logcat 命令执行失败")
            raise AssertionError("adb logcat 命令执行失败:" + result)

    def _initMinicap(self):
        pass

    def _getEndTimeByMiniCap(self):
        pass

    def elementDisplay(self, way, value, timeflag):
        try:
            t = int(timeflag)
            begin = int(time.time())
            end = 0
            while end < (begin + t):
                if self.findView(way, value).is_displayed():
                    return True
            logger.info("超时未找到");
            return False
        except Exception as e:
            logger.info("元素未找到" + e.__doc__)
            return False

    def isElementDisplay(self, way, value, timeFlag):
        if self.elementDisplay(way, value, timeFlag) is True:
            return True
        else:
            return False

    def isElementNotDisplay(self, way, value, timeFlag):
        if self.elementDisplay(way, value, timeFlag) is False:
            return True
        else:
            return False

    def getVerion(self):
        # 当前手机的Android版本
        release_version = self.execShell("shell getprop ro.build.version.release")
        logger.info("当前手机版本为" + release_version)
        return int(release_version.split('.')[0])

    def waitElementDisplay(self, way, value, timeo='30'):
        try:
            begin = int(time.time())
            end = 0
            if way == "IMAGE":
                t = int(timeo)
                while end < (begin + t):
                    a = self.Region_picture_assertion_alone(value)
                    if a == 1:
                        pass
                    else:
                        break
                if end < (begin + t):
                    raise AssertionError("元素" + value + "存在超时")
            elif way == "DOUBLE_IMAGE":

                m = value.split(",")
                t = int(timeo)
                while time.time() < (begin + t):
                    a = self.Region_picture_assertion_double(m[1], m[0])
                    if a == 1:
                        pass
                    else:
                        break
                if end < (begin + t):
                    raise AssertionError("元素" + value + "存在超时")
            else:
                t = int(timeo)
                while time.time() < (begin + t):
                    try:
                        self.findViewfortime(way, value).is_displayed()
                        break
                    except:
                        pass
                if time.time() > (begin + t):
                    raise AssertionError("元素" + value + "存在超时")
                logger.info("元素成功不显示")
        except Exception as e:
            raise e

    def waitElementNotDisplay(self, way, value, timeo='30'):
        '''
          判断元素是否存在
        '''
        try:
            begin = int(time.time())
            end = 0
            if way == "IMAGE":
                t = int(timeo)
                while end < (begin + t):
                    a = self.Region_picture_assertion_alone(value)
                    if a == 1:
                        pass
                    else:
                        break
                if end < (begin + t):
                    raise AssertionError("元素" + value + "存在超时")
            elif way == "DOUBLE_IMAGE":

                m = value.split(",")
                t = int(timeo)
                while time.time() < (begin + t):
                    a = self.Region_picture_assertion_double(m[1], m[0])
                    if a == 1:
                        pass
                    else:
                        break
                if end < (begin + t):
                    raise AssertionError("元素" + value + "存在超时")
            else:
                t = int(timeo)
                while end < (begin + t):
                    try:
                        self.findViewfortime(way, value).is_displayed()
                    except:
                        break
                if end > (begin + t):
                    raise AssertionError("元素" + value + "存在超时")
                logger.info("元素成功不显示")
        except Exception as e:
            raise e

    def waitElementNotExist(self, way, value, timeo='30'):
        '''
          判断元素是否存在
        '''
        try:
            if way == "IMAGE":
                a = self.Region_picture_assertion_alone(value)
                if a == 1:
                    pass
                else:
                    raise AssertionError("断言元素" + value + "超时")
            elif way == "DOUBLE_IMAGE":
                m = value.split(",")
                a = self.Region_picture_assertion_double(m[1], m[0])
                if a == 1:
                    pass
                else:
                    raise AssertionError("断言元素" + value + "超时")
            else:
                a = self.untilTime(way, value, timeo)
                if a:
                    pass
                else:
                    raise AssertionError("断言元素超时")
        except Exception as e:
            raise e

    def ut_assertEqual(self):
        try:
            expectResult = self.driver.find_element
            return 1
        except Exception as e:
                raise e