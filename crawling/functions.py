from selenium.webdriver.common.by import By
import time
import csv


def scroll_down_box_to_bottom(driver, box_xpath):
    # 특정 상자(DIV) 요소 찾기
    box_element = driver.find_element(By.XPATH, box_xpath)

    # 현재 상자(DIV) 내의 항목 개수 확인
    items = []
    last_count = len(box_element.find_elements(By.XPATH, "./*"))

    # 계속 스크롤하면서 새로운 항목이 로드될 때까지 대기
    while True:
        try:
            # 상자(DIV) 요소를 기준으로 아래로 스크롤
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", box_element)

            # 스크롤 후 대기
            time.sleep(2)  # 필요에 따라 대기 시간 조정

            # 현재 상자(DIV) 내의 항목 개수 확인
            current_count = len(box_element.find_elements(By.XPATH, "./*"))

            # 새로운 항목이 로드되지 않으면 반복 중지
            if current_count == last_count:
                break

            last_count = current_count  # 항목 개수 업데이트
        except:
            print("unexpected error during loading reviews")


def scroll_to_bottom(driver):
    # 페이지 높이 구하기
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        try:
            # 페이지 아래로 스크롤
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 페이지 로딩 대기
            time.sleep(2)  # 필요에 따라 대기 시간 조정

            # 새로운 페이지 높이 구하기
            new_height = driver.execute_script("return document.body.scrollHeight")

            # 더 이상 스크롤할 수 없으면 반복 종료
            if new_height == last_height:
                break
            last_height = new_height
        except:
            print('unexpected error during loading lectures')


def csv_to_json(filename):
    data = list()
    with open('crawling/data/' + filename + '.csv', mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for review in csv_reader:
            if review:
                datum = dict()
                datum['lecture'] = review[0]
                datum['professor'] = review[1]
                datum['year'] = int(review[2])
                datum['semester'] = review[3]
                datum['rating'] = int(eval(review[4]))
                datum['comment'] = review[5].replace('\n', '')
                data.append(datum)

    return data
