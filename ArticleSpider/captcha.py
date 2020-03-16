import base64
import time

from zheye import zheye
from mouse import move, click

CN_CAP_XPATH = "//img[@class='Captcha-chineseImg']"
EN_CAP_XPATH = "//img[@class='Captcha-englishImg']"


class ZhihuCaptcha:
    def __init__(self, src):
        self.code = src.replace('data:image/jpg;base64,', '').replace('%0A', '')
        self.cap_file_path = 'captcha.jpg'
        with open(self.cap_file_path, 'wb') as fh:
            fh.write(base64.b64decode(self.code))


class ZhihuCnCaptcha(ZhihuCaptcha):
    def __init__(self, src):
        super().__init__(src)
        self.z = zheye()
        self.xpath = CN_CAP_XPATH
        self.right_positions = self.parse_location()

    def parse_location(self):
        positions = self.z.Recognize(self.cap_file_path)
        positions = [(int(p[1]/2), int(p[0]/2)) for p in positions]
        print('CAPTCHA      positions found.: ', positions)
        return positions

    def process(self, browser):
        element_position = browser.find_element_by_xpath(self.xpath).location
        pannel_height = browser.execute_script('return window.outerHeight-window.innerHeight;')
        print("Start to operate mouse.")
        for position in self.right_positions:
            x = element_position['x'] + position[0]
            y = element_position['y'] + position[1] + pannel_height
            move(x, y)
            print("Mouse: moving to ({}, {})".format(x, y))
            click()
            time.sleep(3)




class ZhihuEnCaptcha(ZhihuCaptcha):
    def __init__(self, src):
        super().__init__(src)
        self.xpath = EN_CAP_XPATH

    def process(self, browser):
        browser.find_element_by_xpath("//input[@name='captcha']").send_keys('1234')
