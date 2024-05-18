# python crawling/crawling_module.py --id [아이디] --pw [비밀번호] --subject [과목명] --out [파일이름]
# 파일 이름은 .csv 없이 입력
# 한글 인코딩 형식 utf-8
# 과목 교수 년도 학기 강의평 순으로 저장
# crawling/data/file.csv에 저장;
# Selenium 4.6부터 사용 가능

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from functions import scroll_to_bottom
import random
from functions import scroll_down_box_to_bottom
from selenium.webdriver.chrome.service import Service
import re, time, json
import argparse
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import csv

semester_dictionary = {'1' : 'Spring', '2': 'Fall', '여' : 'Summer', '겨' : 'Winter'}

parser = argparse.ArgumentParser()
parser.add_argument('--id', required=True)
parser.add_argument('--pw', required=True)

parser.add_argument('--subject', required=True)
parser.add_argument('--out', required=True)


my_id = parser.parse_args().id
my_pw = parser.parse_args().pw
output_file_path = 'crawling/data/'+parser.parse_args().out+'.csv'

#드라이버 객체 생성
driver = webdriver.Chrome()
#웹 페이지 열기
driver.get('https://everytime.kr')
#메뉴 열기
menu_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '/html/body/div/main/header/button'))
)
menu_button.click()
#로그인 창 열기
open_login_button = WebDriverWait(driver,10).until(
    EC.element_to_be_clickable((By.XPATH,'/html/body/div/aside/div[2]/div[1]/a[1]'))
)
open_login_button.click()
#ID, PW 넣어서 로그인
id_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/form/div[1]/input[1]'))
)
id_input.send_keys(my_id)

pw_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div/form/div[1]/input[2]'))
)
pw_input.send_keys(my_pw)

login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div/form/input'))
)
login_button.click()

#강의실 버튼 클릭
classroom_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="menu"]/li[3]/a'))
)
classroom_button.click()

#강좌 검색
my_subject_input = parser.parse_args().subject

subject_searchBox = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH,'/html/body/div/div/div[1]/div/form/input[1]'))
)
subject_searchBox.send_keys(my_subject_input)

subject_searchButton = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH,'/html/body/div/div/div[1]/div/form/input[2]'))
)
subject_searchButton.click()

scroll_to_bottom(driver)

#검색된 강좌의 강의평 링크들 저장
lectures_url_list = []

try:
    lectures = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME,'lecture'))
    )

    for lecture in lectures: # 과목 명에 정확하게 들어맞는, 별점이 있는 강의만 가져오도록
        if lecture.find_element(By.CLASS_NAME,'name').text == parser.parse_args().subject:
            if lecture.find_element(By.CLASS_NAME,'rate').find_element(By.CLASS_NAME,'star').find_element(By.CLASS_NAME,'on').get_attribute('style') != 'width: 0%;':
                lectures_url_list.append(lecture.get_attribute('href'))

except Exception as e:
    print(e)
    print("No Such Subject Found")


#순서대로 링크 방문해서 강의평 크롤링
for lecture_url in lectures_url_list:
    #에타 정지를 피하려면..
    time.sleep(random.randint(3,7))
    driver.get(lecture_url)


    lecture_name = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,'/html/body/div/div/div[2]/div/section[1]/div[1]/a/span'))
    ).text

    try:
        professor = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div/section[1]/div[2]/div/a/span'))
        ).text
    except:
        try:
            professor = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,'/html/body/div/div/div[2]/div/section[1]/div[2]/span'))
            ).text
        except:
            professor = 'Not Determined'

    show_reviews_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div[1]/div[2]/a[2]'))
    )
    show_reviews_button.click()
    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.XPATH,'/html/body/div/div/div[2]/div/div[2]'))
    )
    #모든 리뷰가 로딩될 때까지 scroll down
    scroll_down_box_to_bottom(driver,'/html/body/div/div/div[2]/div/div[2]')

    review_tab = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'articles'))
    )

    reviews = review_tab.find_elements(By.CLASS_NAME,'article')

    with open(output_file_path, mode='a', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        #각 리뷰별로 별점과 강의평 추출
        for review in reviews:
            review_text = review.find_element(By.CLASS_NAME,'text').text
            year_semester = review.find_element(By.CLASS_NAME,'article_header').find_element(By.CLASS_NAME,'title').find_element(By.CLASS_NAME,'info').find_element(By.CLASS_NAME,'semester').text
            year = year_semester[0:2]
            semester = semester_dictionary[year_semester[4]]
            stars = review.find_element(By.CLASS_NAME,'article_header').find_element(By.CLASS_NAME,'title').find_element(By.CLASS_NAME,'rate').find_element(By.CLASS_NAME,'star').find_element(By.CLASS_NAME,'on').get_attribute('style')
            rate = int(stars[-4:-2]) / 20
            if rate == 0: rate = 5.0
            csv_writer.writerow([lecture_name,professor,year,semester,rate,review_text])