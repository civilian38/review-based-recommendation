import time
import csv
import os
import pandas as pd
import shutil
import openai


class UTF_8_SIG:
    """utf-8-sig 변환기
    '\\crawling\\data' 경로상에 있는 모든 csv 파일들을 utf-8-sig로 바꿔주는 함수

    Parameters
    ----------
    file_path_windows : 윈도우상에서 다운로드 받은 파일의 경로
    input_dir : csv 파일의 위치
    output_dir : 변환된 csv 파일의 위치
    wrong_output_dir : 변환되지 않는 csv 파일의 위치
    """
    def __init__(self, file_path_windows, input_dir, output_dir, wrong_output_dir):
        self.file_path_windows = file_path_windows
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.wrong_output_dir = wrong_output_dir
    
    def transformer(self):
        # 시작 시간 기록
        start_time = time.time()
        
        # 입력 디렉토리의 모든 CSV 파일 수를 계산
        csv_files = [f for f in os.listdir(self.input_dir) if f.endswith('.csv')]
        total_files = len(csv_files)
        print(f"총 {total_files}개의 CSV 파일이 발견되었습니다.")
        
        # 처리한 파일 수 초기화
        processed_files = 0
        
        # 입력 디렉토리의 모든 파일에 대해 작업 수행
        for filename in csv_files:
            input_file_path = os.path.join(self.input_dir, filename)
            output_file_path = os.path.join(self.output_dir, filename)
            wrong_output_path = os.path.join(self.wrong_output_dir, filename)
            
            try:
                # CSV 파일을 읽기 (기존 인코딩을 자동 감지)
                df = pd.read_csv(input_file_path, encoding='utf-8')
                
                # 비어 있는 파일 건너뛰기
                if df.empty:
                    print(f"빈 파일입니다. 건너뜁니다: {filename}")
                    shutil.copy2(input_file_path, wrong_output_path)
                    continue
                
                # 줄바꿈 문자를 공백으로 대체
                df = df.map(lambda x: x.replace('\n', ' ') if isinstance(x, str) else x)
                
                # DataFrame을 UTF-8-SIG로 인코딩하여 다시 저장
                df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
                
                processed_files += 1
                if processed_files % (total_files // 10) == 0:
                    progress_percentage = (processed_files / total_files) * 100
                    print(f"변환이 {progress_percentage:.2f}% 진행되었습니다.")
            
            except pd.errors.EmptyDataError:
                print(f"데이터가 없거나 잘못된 형식입니다. 건너뜁니다: {filename}")
                shutil.copy2(input_file_path, wrong_output_path)
                continue
        
        # 총 걸린 시간 계산
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"총 {processed_files}개의 파일이 변환되었습니다.")
        print(f"총 소요 시간: {elapsed_time:.2f} 초")
        
        
        

class OpenAIEmbedding:
    """Openai 임베딩
    '\\embedding\\data\\utf8_sig' 경로상에 있는 모든 csv 파일들에 대해서, 
    6번째 칼럼(강의평)에 해당하는 모든 텍스트를 임베딩해주는 함수

    Parameters
    ----------
    file_path_windows : 윈도우상에서 다운로드 받은 파일의 경로
    input_dir : csv 파일의 위치
    output_dir : 임베딩된 csv 파일의 위치
    wrong_output_dir : 임베딩 되지 않는 csv 파일의 위치
    client : openai 모듈을 사용하기 위한 api 입력변수
    model : openai 모듈중 임베딩에 사용할 모델
    
    functions
    ----------
    text_finder : csv파일을 먼저 읽고, 여섯 번째 칼럼에 있는 모든 텍스트를 texts로 읽어주는 함수
    get_embeddings : texts로 읽힌 파일에 대해서, 각 행별로 임베딩해주는 함수
    csv_out : 임베딩벡터를 기존의 csv파일과 합쳐서 새로운 csv파일에 저장해주는 함수
    process_files : input_dir 경로상에 있는 모든 csv파일들을 임베딩화해주는 함수
    """
    def __init__(self, file_path_windows, input_dir, output_dir, wrong_output_dir):
        self.file_path_windows = file_path_windows
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.wrong_output_dir = wrong_output_dir
        self.client = openai.OpenAI()
        self.model = "text-embedding-3-small"
    
    def text_finder(self, input_file_path):
        df = pd.read_csv(input_file_path, encoding='utf-8-sig', header = None)
        texts = df.iloc[:, 5].tolist()
        return df, texts
        
    def get_embeddings(self, texts):
        embeddings = []
        for i, text in enumerate(texts):
            response = self.client.embeddings.create(input=text, model=self.model)
            # print(f"{i+1} 번째 리뷰 임베딩완료")
            embedding = response.data[0].embedding
            embeddings.append(embedding)
        return embeddings
    
    def csv_out(self, df, embeddings, output_file_path):
        embeddings_df = pd.DataFrame(embeddings)
        result_df = pd.concat([df, embeddings_df], axis=1)
        result_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
        # print(f"임베딩 결과가 저장되었습니다: {output_file_path}")
        
    def process_files(self):
        # 시작 시간 기록
        start_time = time.time()
        
        # 입력 디렉토리의 모든 CSV 파일 수를 계산
        csv_files = [f for f in os.listdir(self.input_dir) if f.endswith('.csv')]
        total_files = len(csv_files)
        print(f"총 {total_files}개의 CSV 파일이 발견되었습니다.")
        
        # 처리한 파일 수 초기화
        processed_files = 0
        
        for filename in csv_files:
            input_file_path = os.path.join(self.input_dir, filename)
            output_file_path = os.path.join(self.output_dir, filename)
            wrong_output_path = os.path.join(self.wrong_output_dir, filename)
            
            try:
                df, texts = self.text_finder(input_file_path)
                embeddings = self.get_embeddings(texts)
                self.csv_out(df, embeddings, output_file_path)
                processed_files += 1
                if processed_files % (total_files // 10) == 0:
                    progress_percentage = (processed_files / total_files) * 100
                    print(f"변환이 {progress_percentage:.2f}% 진행되었습니다.")
                
            except Exception as e:
                print(f"파일 처리 중 오류 발생: {filename}, 오류: {e}")
                shutil.copy2(input_file_path, wrong_output_path)
        
        # 총 걸린 시간 계산
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"총 {processed_files}개의 파일이 임베딩되었습니다.")
        print(f"총 소요 시간: {elapsed_time:.2f} 초")