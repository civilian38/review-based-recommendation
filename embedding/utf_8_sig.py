import sys, os
sys.path.append(os.pardir)
from functions import UTF_8_SIG

# 클래스 인스턴스화
file_path_windows = 'c:\\Users\\SAMSUNG\\review-based-recommendation'
input_dir = file_path_windows + '\\crawling\\data'
output_dir = file_path_windows + '\\embedding\\data\\utf8_sig'
wrong_output_dir = file_path_windows + '\\embedding\\data\\wrong_files'

# 경로 존재하지 않을시 경로 생성
if not os.path.exists(output_dir):
    os.makedirs(output_dir)    
if not os.path.exists(wrong_output_dir):
    os.makedirs(wrong_output_dir)

# 경로내에 있는 파일전체에 대해 utf-8-sig 변환
converter = UTF_8_SIG(file_path_windows, input_dir, output_dir, wrong_output_dir)
converter.transformer()