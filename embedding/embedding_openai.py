import openai
import sys, os
sys.path.append(os.pardir)
import shutil
from functions import OpenAIEmbedding

# 클래스 인스턴스화 및 파일 처리
file_path_windows = 'c:\\Users\\SAMSUNG\\review-based-recommendation'
input_dir = file_path_windows + '\\embedding\\data\\utf8_sig'
output_dir = file_path_windows + '\\embedding\\data\\Embedding'
wrong_output_dir = file_path_windows + '\\crawling\\data\\wrong_embeddings'

# 경로 존재하지 않을시 경로 생성
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(wrong_output_dir):
    os.makedirs(wrong_output_dir)

# 경로내에 있는 파일전체에 대해 임베딩
embedding_processor = OpenAIEmbedding(file_path_windows, input_dir, output_dir, wrong_output_dir)
embedding_processor.process_files()