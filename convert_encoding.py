# convert_encoding.py

def convert_to_utf8(file_path):
    try:
        with open(file_path, 'r', encoding='cp949', errors='ignore') as file:
            content = file.read()
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            
        print(f"{file_path} 파일이 UTF-8로 변환되었습니다.")
    except Exception as e:
        print(f"파일 변환 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    convert_to_utf8('requirements.txt')
