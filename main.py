# _*_ coding:utf-8 _*_
import os,time
import pytest
import argparse

def run_test1():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-appPath', required=False, type=str)
    parser.add_argument('-appiumPort', required=False, type=str)
    parser.add_argument('-appPackage', required=False, type=str)
    parser.add_argument('-appActivity', required=False, type=str)
    parser.add_argument('-serial', required=False, type=str)
    parser.add_argument('-brand', required=False, type=str)

    args = parser.parse_args()
    if args.appPath != None:
        os.environ['appPath'] = args.appPath
    if args.appiumPort != None:
        os.environ['appiumPort'] = args.appiumPort
    if args.appPackage != None:
        os.environ['appPackage'] = args.appPackage
    if args.appActivity != None:
        os.environ['appActivity'] = args.appActivity
    if args.serial != None:
        os.environ['serial'] = args.serial
    if args.brand != None:
        os.environ['brand'] = args.brand

    currentPath = os.path.dirname(os.path.abspath(__file__))
    # date = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
    report_path = os.path.join(currentPath , 'test-output')
    test_folder = os.path.join(currentPath , 'src/testcase/')
    print(test_folder)
    pytest.main([test_folder,'--alluredir=%s' %(report_path)])

def run_test2():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-appPath', required=False, type=str)
    parser.add_argument('-appiumPort', required=False, type=str)
    parser.add_argument('-appPackage', required=False, type=str)
    parser.add_argument('-appActivity', required=False, type=str)
    parser.add_argument('-serial', required=False, type=str)
    parser.add_argument('-brand', required=False, type=str)

    args = parser.parse_args()
    if args.appPath != None:
        os.environ['appPath'] = args.appPath
    if args.appiumPort != None:
        os.environ['appiumPort'] = args.appiumPort
    if args.appPackage != None:
        os.environ['appPackage'] = args.appPackage
    if args.appActivity != None:
        os.environ['appActivity'] = args.appActivity
    if args.serial != None:
        os.environ['serial'] = args.serial
    if args.brand != None:
        os.environ['brand'] = args.brand

    currentPath = os.path.dirname(os.path.abspath(__file__))
    # date = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())
    report_path = os.path.join(currentPath , 'test-output')
    test_folder = os.path.join(currentPath , 'src/testcase/')
    print(test_folder)
    pytest.main([test_folder,'--alluredir=%s' %(report_path)])

if __name__ == "__main__":
    run_test1()
    run_test2()
