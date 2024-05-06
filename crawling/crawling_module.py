# Path: crawling_model.py
# python crawling_model.py --id [아이디] --pw [비밀번호] --subject [과목명] --professor [교수명]

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import re, time, json
from pandas import DataFrame
import pandas as pd
import numpy as np
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import argparse
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

parser = argparse.ArgumentParser()
parser.add_argument('--id', required=True)
parser.add_argument('--pw', required=True)
parser.add_argument('--subject', required=True)
parser.add_argument('--professor', required=True)


my_id = parser.parse_args().id
my_pw = parser.parse_args().pw

ser = Service(EdgeChromiumDriverManager().install())
#드라이버 객체 생성
browser = webdriver.Edge(service=ser)
#에브리타임 주소 입력
browser.get('https://everytime.kr')

# Edge 웹 드라이버 설치 및 인스턴스 생성
ser = Service(EdgeChromiumDriverManager().install())
browser = webdriver.Edge(service=ser)

# 웹 페이지 열기
browser.get('https://everytime.kr')

# "메뉴 열기" 버튼 클릭
menu_button = WebDriverWait(browser, 10).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div/main/header/button'))
)
menu_button.click()

# "로그인" 링크 클릭
login_link = WebDriverWait(browser, 10).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div/aside/div[2]/div[1]/a[1]'))
)
login_link.click()


id_input = WebDriverWait(browser, 3).until(
    EC.presence_of_element_located((By.NAME, 'id'))
)
id_input.send_keys(my_id)

pw_input = WebDriverWait(browser, 3).until(
    EC.presence_of_element_located((By.NAME, 'password'))
)
pw_input.send_keys(my_pw)

submit_button = WebDriverWait(browser, 3).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/form/input'))
)
submit_button.click()

# 강의실 버튼 클릭
classroom_button = WebDriverWait(browser, 20).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/nav/div/ul/li[3]/a'))
)
classroom_button.click()

# 강좌 검색
my_subject_input = parser.parse_args().subject
my_subject_professor = parser.parse_args().professor

subject_input = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[1]/div/form/input[1]'))
)

subject_input.send_keys(my_subject_input)

search_button = WebDriverWait(browser, 10).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[1]/div/form/input[2]'))
)
search_button.click()


# 교수 이름을 html에서 찾아서, 해당 div의 name을 찾아서 그 부분을 클릭
# 해당 교수의 강의가 여러개일 수 있으니까 이를 list로 받아서 클릭할 수 있게 구현
# 교수 이름을 입력하면 해당 교수의 강의를 모두 찾아서 해당 링크를 미리 저장해놓고, 이를 클릭하는 방식으로 구현
def find_professor(professor_name):
    professor_list = browser.find_elements(By.CLASS_NAME, 'professor')
    professor_link_list = []
    for professor in professor_list:
        if professor.text == professor_name:
            professor_link_list.append(professor)
    return professor_link_list

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
        except TimeoutException:
            attempts += 1
            if attempts >= max_attempts: # 시도 횟수 초과 시 종료
                break

            print("Waiting a bit longer for page to load...")
            time.sleep(5)  # 추가 대기 시간


# 스크롤 맨 아래로 내리기
scroll_to_bottom(browser)
# 로딩 시간 대기
WebDriverWait(browser, 5).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'professor'))
)

def safe_click(element):
    try:
        # 요소가 클릭 가능할 때까지 대기
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable(element))
        # 요소 클릭
        element.click()
    except ElementClickInterceptedException:
        # 요소가 화면에 보이도록 스크롤
        browser.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)  # 잠시 대기 후 클릭
        # 다시 클릭 시도
        element.click()
    except Exception as e:
        # JavaScript를 사용한 클릭
        browser.execute_script("arguments[0].click();", element)
# 교수 이름 클릭
professor_link_list = find_professor(my_subject_professor)
if professor_link_list:
    safe_click(professor_link_list[0])

# 강의평 더보기 클릭
more_review_button = WebDriverWait(browser, 10).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[2]/div/section[2]/div[3]/a'))
)
more_review_button.click()

# 스크롤 맨 아래로 내리기
scroll_to_bottom(browser, max_attempts=5)

def get_reviews(browser):
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'article'))
    )
    review_elements = browser.find_elements(By.CLASS_NAME, 'article')
    reviews = []

    for element in review_elements:
        try:
            # 텍스트 요소 대기 및 찾기
            text_element = WebDriverWait(element, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'text'))
            )
            review_text = text_element.text

            # 별점 추출
            star_element = element.find_element(By.CSS_SELECTOR, '.star .on')
            star_style = star_element.get_attribute('style')
            star_percentage = re.findall(r'width: (\d+)%;', star_style)[0]
            #

            reviews.append({'text': review_text, 'stars': int(star_percentage)})
        except Exception as e:
            print(f"Error processing review element: {str(e)}")
            continue

    return reviews


reviews = get_reviews(browser)

# review를 json 파일로 저장
with open(my_subject_input + '_' + my_subject_professor + '.json', 'w', encoding='utf-8') as f:
    json.dump(reviews, f, ensure_ascii=False, indent=4)

# review를 pandas DataFrame으로 변환
# df = DataFrame(reviews)
# df.to_csv(my_subject_input + '_' + my_subject_professor + '.csv', index=False, encoding='utf-8-sig')

# 브라우저 종료
browser.quit()