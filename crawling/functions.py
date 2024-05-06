import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
def scroll_to_bottom(browser, max_attempts=3):
    last_height = browser.execute_script("return document.body.scrollHeight")
    attempts = 0  # 시도 횟수 카운터

    while True:
        # 스크롤 다운
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # 페이지 로드 대기 시간

        try:
            # 스크롤이 더이상 변화가 없는지 확인
            WebDriverWait(browser, 10).until(
                lambda browser: browser.execute_script("return document.body.scrollHeight") > last_height
            )
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        except:
            attempts += 1
            if attempts >= max_attempts: # 시도 횟수 초과 시 종료
                break

            print("Waiting a bit longer for page to load...")
            time.sleep(5)  # 추가 대기 시간