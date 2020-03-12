from selenium import webdriver

browser = webdriver.Chrome(executable_path='/usr/bin/chromedriver')

browser.get('https://www.zhihu.com/signin')

browser.find_element_by_xpath("//div[@class='SignFlow-tab']").click()
browser.find_element_by_xpath("//input[@name='username']").send_keys('18965150181')
browser.find_element_by_xpath("//input[@name='password']").send_keys('pachong101')
browser.find_element_by_xpath("//button[@class='Button SignFlow-submitButton Button--primary Button--blue']") \
    .click()

