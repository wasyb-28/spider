from selenium import webdriver
from selenium.webdriver.support.select import Select

browser = webdriver.Chrome()
browser.get('http://data.stats.gov.cn/easyquery.htm?cn=G0104')
print(0)
# 选择指标
browser.find_element_by_id('treeZhiBiao_4_a').click()
print(1)
# 选择时间
browser.find_element_by_id('mySelect_sj').click()
print(2)
browser.find_element_by_xpath('//div[@class="dtBody"]/div[1]/ul/li[15]').click()
print(3)
