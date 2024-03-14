import time
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import csv
from bs4 import BeautifulSoup as bs

# Если используется прокси записать в формате login:password@ip:port либо же ip:port
proxy = None


class Selenium:
    def __init__(self, proxy) -> None:
        self.driver = None
        self.proxy = proxy

    def start_driver(self):
        '''Функция старта драйвера'''
        options = webdriver.ChromeOptions()
        options.add_argument('--no-first-run')
        options.add_argument('--no-service-autorun')
        options.add_argument('--password-store=basic')
        if proxy is not None:
            options.add_argument(f'--proxy-server={proxy}')
        driver = uc.Chrome(
            options=options
        )
        self.driver = driver
        return driver

    def take_element(self, path, timeout=20, delay=0):
        '''функция для клика по элементу'''
        try:
            time.sleep(delay)
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, path))).click()

        except Exception as e:
            print(f"No element after {timeout} seconds of waiting!!!\n{path}")
            return None

    def open_site(self, url):
        '''Функция для открытия сайта'''
        self.driver.get(url)

    def hover(self, path, timeout=20, delay=0):
        '''Функция новедения курсора на элемент'''
        action = ActionChains(self.driver)
        element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, path)))
        time.sleep(delay)
        action.move_to_element(element).perform()

    def select_value(self, path, value, timeout=20, delay=0):
        '''Функция для выбора значения в селекторе'''
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, path)))
        time.sleep(delay)
        element = self.driver.find_element(By.XPATH, path)
        Select(element).select_by_visible_text(value)

    def scroll(self, step, delay=5):
        '''Функция скролла'''
        time.sleep(delay)
        self.driver.execute_script(f"window.scrollBy(0, {step})")


class NseIndia(Selenium):
    def __init__(self, driver) -> None:
        self.driver = driver
        pass

    def open_market_data(self):
        '''Открываем страницу для парсинга'''
        self.open_site('https://www.nseindia.com/')
        self.hover('//*[@id="main_navbar"]/ul/li[3]')
        self.take_element('//*[@id="main_navbar"]/ul/li[3]/div/div[1]/div/div[1]/ul/li[1]/a', delay=2)
        self.select_value('//*[@id="sel-Pre-Open-Market"]', 'All') #По ТЗ не совсем понял какие именно значения нужно парсить, поэтому выбрал в селекторе все, если нужно именно  NIFTY 50 эту строчку удалить
        time.sleep(10)

        source = self.driver.page_source
        return source

    def parsing_price(self, source):
        '''Парсим данные и заносим их в csv таблицу'''
        soup = bs(source, 'html.parser')
        names = soup.find_all(class_='symbol-word-break')
        prices = soup.find_all(class_='bold text-right')[1:]

        with open('output.csv', 'w', newline='') as csvfile:
            fieldnames = ['Name', 'Price']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for name, price in zip(names, prices):
                writer.writerow({'Name': name.text.strip(), 'Price': price.text.strip()})

    def action_emulation(self):
        '''Эмулируем какие либо пользовательские действия на сайте'''
        self.take_element('/html/body/header/nav/div[1]/a/img')
        self.take_element('//*[@id="tabList_NIFTYBANK"]', delay=5)
        self.scroll(800)
        self.take_element('//*[@id="tab4_gainers_loosers"]/div[3]/a',delay=2)
        self.select_value('//*[@id="equitieStockSelect"]', 'NIFTY ALPHA 50', delay=5)
        scroll_height = self.driver.execute_script("return document.body.scrollHeight;")
        for i in range(10):
            scroll_step = scroll_height / 10
            self.scroll(int(scroll_step), delay=0.5)


def worker():
    driver_session = Selenium(proxy)
    driver = driver_session.start_driver()
    nsemedia = NseIndia(driver)
    source = nsemedia.open_market_data()
    nsemedia.parsing_price(source)
    nsemedia.action_emulation()
    driver.close()
    driver.quit()


if __name__ == '__main__':
    worker()
