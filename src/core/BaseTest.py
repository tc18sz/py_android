import platform
from configparser import ConfigParser

import allure
from appium import webdriver
import os
from src.field.Elements import Elements
from src.utils.loggers import JFMlogging
from src.core.DT import DT


class BaseTest():
    def after(self):
        self.f = ""

    elements = Elements()
    logger = JFMlogging().getloger()

    def new(self, list1):
        caseName = os.environ.get('PYTEST_CURRENT_TEST').split('::')[-1]
        if " (" in caseName and "[" not in caseName:
            self.caseName = caseName.split(" (")[0]
        elif "[" in caseName and "]" in caseName:
            self.caseName = caseName.split("[")[0]
        self.listEnd = list1[self.caseName]
        self.after()

    def execComm(self, text):
        import subprocess
        import traceback
        try:

            obj = subprocess.Popen(text, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            obj.wait()

            lines = obj.stdout.readlines()

            if not lines or len(lines) == 0:
                line = obj.stderr.readlines()
                return None
            # for i in lines:
            #     print(i.encode('utf-8'))

            unicode_text = u''

            if (len(lines) == 1):
                unicode_text = unicode_text + lines[0].decode('utf-8')
                print(unicode_text)
                return unicode_text
            else:
                version = (unicode_text + lines[0].decode('utf-8')).split("versionName=")[1].split("'")[1]
                name = (unicode_text + lines[1].decode('utf-8')).split("'")[1]
                rr = [version, name]
                return rr

        except Exception as e:
            print(traceback.format_exc())

    def getPhone(self):
        serial = os.getenv("serial")
        brand_series = os.getenv("brand")
        appPath = os.environ.get('appPath')
        result = ""
        if str(serial) == "" or serial is None:
            command = "adb "
        else:
            command = "adb -s {0} ".format(serial)
        if platform.system().lower() == 'windows':
            findstr = "| findstr /c:application-label-zh-CN /c:version"
        else:
            findstr = "| grep -E 'application-label-zh-CN|versionName'"

        brand = self.execComm(command + "shell getprop ro.product.brand")
        model = self.execComm(command + "shell getprop ro.product.model")
        release = self.execComm(command + "shell getprop ro.build.version.release")

        if str(appPath) == "" or appPath is None:
            result = "品牌: {}型号: {}版本号: {}".format(brand, model, release)
        else:
            r = "aapt dump badging {} {} ".format(appPath, findstr)
            rr = self.execComm(r)
            if (rr != None):
                result = "品牌: {}型号: {}版本号: {}测试包名称: {}\n测试包版本: {}".format(brand, model, release, rr[1], rr[0])

        if (brand_series != "" and brand_series != None):
            result = result + "\n品牌系列: " + brand_series
        return result

    def setUp(self):
        result = self.getPhone()
        currentPath = os.path.dirname(os.path.abspath(__file__))
        root_path1 = os.path.abspath(os.path.join(currentPath, "../.."))
        config_data = os.path.join(root_path1, 'config.properties')
        print(config_data)
        conf = ConfigParser()
        conf.read(config_data)
        with allure.step("设备信息"):
            allure.attach(result)
        if os.environ.get('appPath') == None:
            try:

                if (conf.get("SectionA", "apptype") == '1'):
                    self.desired_caps = {}
                    self.desired_caps['platformName'] = 'Android'  # 平台
                    self.desired_caps['platformVersion'] = conf.get("SectionA", "platformVersion")  # 系统版本
                    # self.desired_caps['app'] = 'E:/autotestingPro/app/UCliulanqi_701.apk'   # 指向.apk文件，如果设置appPackage和appActivity，那么这项会被忽略
                    self.desired_caps['appPackage'] = conf.get("SectionA", "appPackage")  # APK包名
                    self.desired_caps['appActivity'] = conf.get("SectionA", "appActivity")  # 被测程序启动时的Activity
                    #self.desired_caps['unicodeKeyboard'] = True  # 是否支持unicode的键盘。如果需要输入中文，要设置为“true”
                    #self.desired_caps['resetKeyboard'] = True  # 是否在测试结束后将键盘重轩为系统默认的输入法。
                    self.desired_caps['newCommandTimeout'] = '120'  # Appium服务器待appium客户端发送新消息的时间。默认为60秒
                    self.desired_caps['deviceName'] = conf.get("SectionA", "deviceName")  # 手机ID
                    self.desired_caps['noReset'] = True  # true:不重新安装APP，false:重新安装app
                    self.desired_caps['sessionOverride'] = True  # true:覆盖session，false:不覆盖session
                    self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", self.desired_caps)
                    self.driver.implicitly_wait(2)
                    self.dt = DT(self.driver, self)
                    return self.driver, self.dt
                elif (conf.get("SectionA", "apptype") == '2'):
                    self.desired_caps = {}
                    self.desired_caps['platformName'] = 'Android'  # 平台
                    self.desired_caps['platformVersion'] = conf.get("SectionA", "platformVersion")  # 系统版本
                    # self.desired_caps['app'] = 'E:/autotestingPro/app/UCliulanqi_701.apk'   # 指向.apk文件，如果设置appPackage和appActivity，那么这项会被忽略
                    self.desired_caps['appPackage'] = "com.tencent.mm"  # APK包名
                    self.desired_caps['appActivity'] = "ui.LauncherUI"  # 被测程序启动时的Activity
                    self.desired_caps['unicodeKeyboard'] = True  # 是否支持unicode的键盘。如果需要输入中文，要设置为“true”
                    self.desired_caps['resetKeyboard'] = True  # 是否在测试结束后将键盘重轩为系统默认的输入法。
                    self.desired_caps['newCommandTimeout'] = '120'  # Appium服务器待appium客户端发送新消息的时间。默认为60秒
                    self.desired_caps['deviceName'] = conf.get("SectionA", "deviceName")  # 手机ID
                    self.desired_caps['noReset'] = True  # true:不重新安装APP，false:重新安装app
                    self.desired_caps['sessionOverride'] = True  # true:覆盖session，false:不覆盖session
                    self.desired_caps['chromeOptions'] = {'androidProcess': 'com.tencent.mm:tools'}  # 关键所在
                    # self.desired_caps['AUTOMATION_NAME'] = 'uiautomator2'
                    self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", self.desired_caps)
                    self.driver.implicitly_wait(2)
                    self.dt = DT(self.driver, self)
                    return self.driver, self.dt
            except Exception as e:
                raise e
        else:

            self.desired_caps = {}
            self.desired_caps['platformName'] = 'Android'  # 平台
            self.desired_caps['platformVersion'] = conf.get("SectionA", "platformVersion")  # 系统版本
            # self.desired_caps['app'] = 'E:/autotestingPro/app/UCliulanqi_701.apk'   # 指向.apk文件，如果设置appPackage和appActivity，那么这项会被忽略
            self.desired_caps['appPackage'] = os.environ.get('appPackage')  # APK包名
            if os.environ.get('appActivity') == "":
                self.desired_caps['appActivity'] = "com.google.android.apps.chrome.Main" # 被测程序启动时的Activity
            else:
                self.desired_caps['appActivity'] = os.environ.get("appActivity")
            #self.desired_caps['unicodeKeyboard'] = True  # 是否支持unicode的键盘。如果需要输入中文，要设置为“true”
            #self.desired_caps['resetKeyboard'] = True  # 是否在测试结束后将键盘重轩为系统默认的输入法。
            self.desired_caps['newCommandTimeout'] = '120'  # Appium服务器待appium客户端发送新消息的时间。默认为60秒
            self.desired_caps['deviceName'] = os.environ.get('serial')  # 手机ID
            self.desired_caps['noReset'] = True  # true:不重新安装APP，false:重新安装app
            self.desired_caps['sessionOverride'] = True  # true:覆盖session，false:不覆盖session
            self.desired_caps['app'] = os.environ.get('appPath')
            self.desired_caps['androidInstallTimeout'] = 180000
            self.desired_caps['skipDeviceInitialization'] = True
            self.desired_caps['skipServerInstallation'] = True
            self.driver = webdriver.Remote("http://127.0.0.1:" + os.environ.get('appiumPort') + "/wd/hub",
                                           self.desired_caps)
            self.driver.implicitly_wait(2)
            self.dt = DT(self.driver, self)
            return self.driver, self.dt

    def setUp_bak(self):
        result = self.getPhone()
        currentPath = os.path.dirname(os.path.abspath(__file__))
        root_path1 = os.path.abspath(os.path.join(currentPath, "../.."))
        config_data = os.path.join(root_path1, 'config.properties')
        print(config_data)
        conf = ConfigParser()
        conf.read(config_data)
        with allure.step("设备信息"):
            allure.attach(result)
        if os.environ.get('appPath') == None:
            try:

                if (conf.get("SectionA", "apptype") == '1'):
                    self.desired_caps = {}
                    self.desired_caps['platformName'] = 'Android'  # 平台
                    self.desired_caps['platformVersion'] = conf.get("SectionA", "platformVersion")  # 系统版本
                    # self.desired_caps['app'] = 'E:/autotestingPro/app/UCliulanqi_701.apk'   # 指向.apk文件，如果设置appPackage和appActivity，那么这项会被忽略
                    self.desired_caps['appPackage'] = conf.get("SectionA", "appPackage")  # APK包名
                    self.desired_caps['appActivity'] = conf.get("SectionA", "appActivity")  # 被测程序启动时的Activity
                    #self.desired_caps['unicodeKeyboard'] = True  # 是否支持unicode的键盘。如果需要输入中文，要设置为“true”
                    #self.desired_caps['resetKeyboard'] = True  # 是否在测试结束后将键盘重轩为系统默认的输入法。
                    self.desired_caps['newCommandTimeout'] = '120'  # Appium服务器待appium客户端发送新消息的时间。默认为60秒
                    self.desired_caps['deviceName'] = conf.get("SectionA", "deviceName")  # 手机ID
                    self.desired_caps['noReset'] = True  # true:不重新安装APP，false:重新安装app
                    self.desired_caps['sessionOverride'] = True  # true:覆盖session，false:不覆盖session
                    self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", self.desired_caps)
                    self.driver.implicitly_wait(2)
                    self.dt = DT(self.driver, self)
                    return self.driver, self.dt
                elif (conf.get("SectionA", "apptype") == '2'):
                    self.desired_caps = {}
                    self.desired_caps['platformName'] = 'Android'  # 平台
                    self.desired_caps['platformVersion'] = conf.get("SectionA", "platformVersion")  # 系统版本
                    # self.desired_caps['app'] = 'E:/autotestingPro/app/UCliulanqi_701.apk'   # 指向.apk文件，如果设置appPackage和appActivity，那么这项会被忽略
                    self.desired_caps['appPackage'] = "com.tencent.mm"  # APK包名
                    self.desired_caps['appActivity'] = "ui.LauncherUI"  # 被测程序启动时的Activity
                    self.desired_caps['unicodeKeyboard'] = True  # 是否支持unicode的键盘。如果需要输入中文，要设置为“true”
                    self.desired_caps['resetKeyboard'] = True  # 是否在测试结束后将键盘重轩为系统默认的输入法。
                    self.desired_caps['newCommandTimeout'] = '120'  # Appium服务器待appium客户端发送新消息的时间。默认为60秒
                    self.desired_caps['deviceName'] = conf.get("SectionA", "deviceName")  # 手机ID
                    self.desired_caps['noReset'] = True  # true:不重新安装APP，false:重新安装app
                    self.desired_caps['sessionOverride'] = True  # true:覆盖session，false:不覆盖session
                    self.desired_caps['chromeOptions'] = {'androidProcess': 'com.tencent.mm:tools'}  # 关键所在
                    # self.desired_caps['AUTOMATION_NAME'] = 'uiautomator2'
                    self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", self.desired_caps)
                    self.driver.implicitly_wait(2)
                    self.dt = DT(self.driver, self)
                    return self.driver, self.dt
            except Exception as e:
                raise e
        else:

            self.desired_caps = {}
            self.desired_caps['platformName'] = 'Android'  # 平台
            # self.desired_caps['platformVersion'] = conf.get("SectionA", "platformVersion")  # 系统版本
            # self.desired_caps['app'] = 'E:/autotestingPro/app/UCliulanqi_701.apk'   # 指向.apk文件，如果设置appPackage和appActivity，那么这项会被忽略
            self.desired_caps['appPackage'] = os.environ.get('appPackage')  # APK包名
            if os.environ.get('appActivity') == "":
                self.desired_caps['appActivity'] = "com.google.android.apps.chrome.Main" # 被测程序启动时的Activity
            else:
                self.desired_caps['appActivity'] = os.environ.get("appActivity")
            self.desired_caps['unicodeKeyboard'] = True  # 是否支持unicode的键盘。如果需要输入中文，要设置为“true”
            self.desired_caps['resetKeyboard'] = True  # 是否在测试结束后将键盘重轩为系统默认的输入法。
            self.desired_caps['newCommandTimeout'] = '120'  # Appium服务器待appium客户端发送新消息的时间。默认为60秒
            self.desired_caps['deviceName'] = os.environ.get('serial')  # 手机ID
            self.desired_caps['noReset'] = True  # true:不重新安装APP，false:重新安装app
            self.desired_caps['sessionOverride'] = True  # true:覆盖session，false:不覆盖session
            self.desired_caps['app'] = os.environ.get('appPath')
            self.desired_caps['androidInstallTimeout'] = 180000
            self.desired_caps['skipDeviceInitialization'] = True
            self.desired_caps['skipServerInstallation'] = True
            self.driver = webdriver.Remote("http://127.0.0.1:" + os.environ.get('appiumPort') + "/wd/hub",
                                           self.desired_caps)
            self.driver.implicitly_wait(2)
            self.dt = DT(self.driver, self)
            return self.driver, self.dt

    def beforeEnd(self):

        if len(self.f) != 0:
            allure.attach(self.f, "statistics", attachment_type=allure.attachment_type.TEXT)
