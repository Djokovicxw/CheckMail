# -*- coding:utf-8 -*-
import os
import sys
import time
import unittest
import json

from aiohttp import web
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from login_swjtu.geetest_slider_crack import *

LOGIN_URL = 'http://dean.vatuu.com/service/login.html'


class Browser(object):

    def __init__(self, driver_path=""):
        option = Options()
        option.add_argument('--headless')
        try:
            self.driver = webdriver.Chrome(options=option)
        except Exception:
            self.driver = webdriver.Chrome(driver_path, options=option)
        except Exception:
            print('Chromedriver Not Found!')
            sys.exit(0)
        self.driver.set_window_size(1920, 1080)

    def on_exit(self):
        self.driver.close()
        self.driver.quit()

    def login(self, data: dict, max_retries=3):
        self.driver: webdriver.Remote
        if 'username' not in data or 'password' not in data:
            return web.json_response(data={'status': -1, 'msg': 'Data Incomplete'})
        self.driver.delete_all_cookies()
        self.driver.get(LOGIN_URL)
        validate_success = False
        login_success = False
        reason = ''
        try:
            slider_selector = show_random_image(self.driver)
            time.sleep(1)
            for i in range(max_retries):
                offset = get_offset(self.driver)
                time.sleep(1)
                gen_actions_and_perform(self.driver, slider_selector, offset)
                validate_success = check_validate_success(self.driver, 5)
                if validate_success:
                    print('validate success')
                    time.sleep(1)
                    login_success = login_after_validate(self.driver, data)
                    if login_success:
                        break
                else:
                    print(f'validate error...try the {i + 1} time')
                    reload_random_image(self.driver)
                    time.sleep(1)
        except TimeoutException:
            reason = 'TimeoutException'
        return {'status': int(validate_success and login_success),
                'JSESSIONID': self.driver.get_cookie('JSESSIONID'),
                'reason': reason}


def login_after_validate(driver, data):
    enter_username_and_password(driver, data)
    clicked = click_login(driver)
    if not clicked:
        return False
    return check_login_success(driver, 5)


def check_login_success(driver, wait_time=5):
    try:
        status = WebDriverWait(driver, wait_time).until(
            expected_conditions.url_changes(LOGIN_URL)
        )
    except TimeoutException:
        status = False
    return status


def enter_username_and_password(driver, data):
    username, password = data.get('username'), data.get('password')
    username_box = driver.find_element_by_css_selector('#username')
    username_box.send_keys(username)
    time.sleep(0.5)  # wait for input complete
    password_box = driver.find_element_by_css_selector('#password')
    password_box.send_keys(password)
    time.sleep(0.5)  # wait for input complete


def click_login(driver):
    login_btn = '#submit2'
    btn = driver.find_element_by_css_selector(login_btn)
    try:
        WebDriverWait(driver, 5).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, login_btn))
        )
        btn.click()
        return True
    except TimeoutException:
        return False


class LoginTest(unittest.TestCase):

    def setUp(self):
        self.browser = Browser()

    def tearDown(self):
        self.browser.on_exit()

    def testLogin(self):
        data = {'username': '', 'password': ''}
        res = self.browser.login(data)
        res_json = json.dumps(res)
        res_json = json.loads(res_json)
        self.assertEqual(1, res_json.get('status'), msg='login success')
        self.assertIsNotNone(res_json.get('JSESSIONID'), msg='got JSESSIONID')
