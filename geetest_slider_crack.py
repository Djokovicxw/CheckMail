# -*- coding:utf-8 -*-
import io
import random
import base64
from math import exp

from PIL import Image, ImageChops, ImageFilter
import numpy
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


class text_to_be_present_in_element_attr(object):
    """
    An expectation for checking if the given text is present in the element's given attr
    """
    def __init__(self, locator: (str, str), text_: str, attr: str):
        self.locator = locator
        self.text = text_
        self.attr = attr

    def __call__(self, driver):
        try:
            element_text = expected_conditions._find_element(driver, self.locator).get_attribute(self.attr)
            if element_text:
                return self.text in element_text
            else:
                return False
        except StaleElementReferenceException:
            return False
        except TimeoutException:
            return False


def check_validate_success(driver, wait_time=5):
    try:
        status = WebDriverWait(driver, wait_time).until(
            text_to_be_present_in_element_attr((By.CSS_SELECTOR, 'div.geetest_radar_tip'), '验证成功', 'aria-label')
        )
    except TimeoutException:
        status = False
    return status


def reload_random_image(driver):
    btn = driver.find_element_by_css_selector('a.geetest_refresh_1')
    btn.click()


def get_offset(driver):
    raw_image, modified_image = get_images(driver)
    offset = calculate_offset(raw_image, modified_image)
    return offset


def show_random_image(driver):
    btn = WebDriverWait(driver, 10).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '#captcha2 > div > div.geetest_btn'))
    )
    btn.click()
    slider_selector = 'div.geetest_slider_button'
    # slider = wait.until(
    #     expected_conditions.presence_of_element_located((By.CSS_SELECTOR, slider_selector))
    # )
    # slider.click()
    return slider_selector


def get_images(driver) -> (Image.Image, Image.Image):
    raw_im_b64 = driver.execute_script(
        "return document.querySelector('div.geetest_canvas_img.geetest_absolute > canvas').toDataURL('image/png');"
    )
    modified_im_b64 = driver.execute_script(
        "return document.querySelector('canvas.geetest_canvas_bg.geetest_absolute').toDataURL('image/png');"
    )

    raw_im_bytes = base64.b64decode(raw_im_b64.rsplit(',', 1)[-1])
    modified_im = base64.b64decode(modified_im_b64.rsplit(',', 1)[-1])

    raw_image = Image.open(io.BytesIO(raw_im_bytes))
    modified_image = Image.open(io.BytesIO(modified_im))

    # raw_image.save('./raw.png')
    # modified_image.save('./modified.png')
    return raw_image, modified_image


def gen_actions_and_perform(driver, slider_selector, offset):
    action_chains = ActionChains(driver)
    moves = gen_smooth_array(offset)
    slider = driver.find_element_by_css_selector(slider_selector)
    action_chains.move_to_element_with_offset(slider, random.randint(5, 10), random.randint(2, 8))
    action_chains.click_and_hold(slider).pause(0.05)
    last = 0
    if random.random() > 0.5:
        direct = 1
    else:
        direct = -1
    for expect in moves:
        y = random.randint(1, 2) * direct
        offset = max(expect - last + random.randint(0, 2), 0)
        action_chains.move_by_offset(offset, y).pause(random.uniform(0.01, 0.02))
        last += offset
    action_chains.pause(random.uniform(0.1, 0.2)).release(slider)
    action_chains.perform()


def gen_smooth_array(offset: int, num: int=20):
    array = [int(sigmoid(x/2, offset)) for x in range(-num, num+1)]
    return array


def sigmoid(x, b):
    return b / (1 + exp(-x * 0.4))


def calculate_offset(raw_image: Image.Image, modified_image: Image.Image) -> float:
    diff = ImageChops.difference(raw_image, modified_image)
    edge = diff.filter(ImageFilter.FIND_EDGES).convert('1')
    edge_arr = numpy.array(edge)
    down_sum = edge_arr.sum(axis=0)
    start, end = sorted(down_sum.argsort()[-2:])
    # show offset line
    # for y in range(modified_image.height):
    #     modified_image.putpixel((start, y), 255)
    # modified_image.show()
    return int(start - 6)  # magic 6 for slider offset
