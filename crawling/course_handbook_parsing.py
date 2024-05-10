import csv
import re

csv_file_path = 'course_handbook_parsed.csv'

txt_file_path = 'c:\\Users\\SAMSUNG\\Downloads\\Downloads\\모델 경량화 프로젝트\\review-based-recommendation-main\\review-based-recommendation-main\\crawling\\data\\course_handbook_txt.txt'

with open(txt_file_path, 'r', encoding='utf-8') as file:
    text = file.read()

# 정규 표현식 : 한글 강의명, 영문 강의명 읽기
pattern = r"(\d+\.\d+)\s+([^\(]+)\(([^\)]+)\)"
courses = re.findall(pattern, text, re.DOTALL)
course_dict = {}

# 결과 정리
for course in courses:
    code, korean_title, english_title = course
    korean_title = ' '.join(korean_title.split())
    english_title = ' '.join(english_title.split())
    course_dict[korean_title] = english_title

# 결과 출력
for k, v in course_dict.items():
    print(f"'{k}': '{v}'")


with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.writer(csvfile)
    # CSV 파일 헤더 작성
    writer.writerow(['한글 강의명', '영문 강의명'])
    # 딕셔너리 키와 값을 순회하면서 CSV 파일 입력
    for korean_title, english_title in course_dict.items():
        writer.writerow([korean_title, english_title])