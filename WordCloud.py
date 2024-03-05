import os
import shutil
import subprocess
from collections import Counter
import tkinter as tk
from tkinter import filedialog
from konlpy.tag import Mecab # 한국어 형태소 분석기 Konlpy의 Mecab 모듈

import numpy as np
import pandas as pd
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from wordcloud import WordCloud, ImageColorGenerator
from jamo import h2j, j2hcj



"""
import chardet
import pycurl
from io import BytesIO

def fetch_url_content(url):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.SSL_VERIFYPEER, False)
    c.setopt(pycurl.HTTPHEADER, [
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ])
    try:
        c.perform()
    except pycurl.error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        c.close()

    # Unicode Decode Error
    raw_data = buffer.getvalue()
    try:
        encoding = chardet.detect(raw_data)['encoding']
        return raw_data.decode(encoding)
    except UnicodeDecodeError:
        try:
            # Try decoding with a different encoding
            return raw_data.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to 'latin-1' or 'ignore' errors
            return raw_data.decode('latin-1', errors='ignore')
"""

def get_jongsung_TF(sample_text):
    sample_text_list = list(sample_text)
    last_word = sample_text_list[-1]
    last_word_jamo_list = list(j2hcj(h2j(last_word)))
    last_jamo = last_word_jamo_list[-1]

    jongsung_TF = "T"

    if last_jamo in ['ㅏ', 'ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ', 'ㅘ', 'ㅚ', 'ㅙ', 'ㅝ', 'ㅞ', 'ㅢ', 'ㅐ', 'ㅔ', 'ㅟ', 'ㅖ', 'ㅒ']:
        jongsung_TF = "F"

    return jongsung_TF


def fetch_contents_from_urls(urls):
    print("Start")
    count= 1
    all_content = ""
    for url in urls:
        content = fetch_url_content_selenium(url, count)  # 앞서 정의한 함수 사용
        count += 1
        if content:
            all_content += " " + content  # 콘텐츠를 모두 합침
    return all_content

def fetch_url_content_selenium(url,count):
    print(count)
    # 셀레니움에서 사용할 Chrom driver 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저 UI 없이 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    content = ""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # 메인 페이지 콘텐츠 가져오기
        content += driver.find_element(By.TAG_NAME, 'body').text
        print(content)
        # 페이지 내의 모든 iframe 처리
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
                content += driver.find_element(By.TAG_NAME, 'body').text
                driver.switch_to.default_content()
            except Exception as e:
                print(f"Error occurred in iframes: {e}")
                # 오류 발생 후 다시 iframe으로 계속 진행(error print만 진행)
                # 해당 문절에서 iframe 오류는 iframe으로 들어갔지만 내용이 없을 때이기 때문에 다시 반복

        return content
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        driver.quit()

# 워드 클라우드를 생성하는 함수입니다.
def generate_wordcloud(content, font, baseImage, ew, tw):
    tword = []
    for check in tw:
        if check != '':
            tword.append(check)
            train_word(tword)

    pos_tagged = Mecab("venv/Lib/site-packages/mecab/tools/mecab-ko-dic").pos(content)

    print("------------------전체 가져온 tag--------------------------")
    print(pos_tagged)
    print("------------------선별된 형태소 tag--------------------------")
    noun_adj_list = [word for word, tag in pos_tagged if tag in ['NNG', 'SL', 'NNP', 'VA+ETM', 'SH']]
    print(noun_adj_list)
    print("------------------최종 단어 제외 후 tag--------------------------")
    exclude_words = ew + ['블로그', '글', '이미지','아이디','검색', '광고', '네이버','이웃','댓글','움','창', '초', '시']
    k_stopword = pd.read_csv('korean_stopword.csv')
    k_stopword = list(k_stopword['불용어'])
    exclude_words = exclude_words +k_stopword


    filtered_words = [word for word in noun_adj_list if word not in exclude_words]

    counts = Counter(filtered_words)
    tags = counts.most_common(1000)

    masking_image = np.array(Image.open("images/{}.png".format(baseImage)))
    print(tags)

    # 워드클라우드 인스턴스 설정
    wc = WordCloud(
        font_path="font/{}/{}.otf".format(font, font),
        mask=masking_image, # 마스크 이미지를 적용합니다.
        background_color='white',
        max_font_size=300,
        min_font_size=1,
        max_words=1000
    ).generate_from_frequencies(dict(tags))

    # 마스크 이미지의 색상을 사용하여 워드 클라우드의 색상을 조정합니다.
    # 글자의 색이 base image의 색과 자연스럽게 어울리게 됨
    image_colors = ImageColorGenerator(masking_image)
    wc = wc.recolor(color_func=image_colors)

    # Save to file
    output_filename = "result/result.png"
    wc.to_file(output_filename)
    print("파일의 위치를 지정해주세요!")
    save_tags_to_file(tags)
    return {"tags": tags, "image_path": output_filename}

def train_word(tw):
    with open('venv/Lib/site-packages/mecab/tools/mecab-ko-dic/NNP.csv', "r", encoding='utf-8') as f:
        user_dict = f.readlines()

    for word in tw:
        jongsung_TF = get_jongsung_TF(word)
        line = '{},*,*,*,NNP,*,{},{},*,*,*,*,*\n'.format(word, jongsung_TF, word)
        user_dict.append(line)

    with open('venv/Lib/site-packages/mecab/tools/mecab-ko-dic/NNP.csv', 'w', encoding='utf-8') as f:
        for line in user_dict:
            f.write(line)
    # csv 파일 수정 후 빌드(꼭 필요)
    subprocess.run(["powershell", "Set-ExecutionPolicy", "Unrestricted", "-Force"], input="y", text=True)
    subprocess.run(["powershell", "cd venv/Lib/site-packages/mecab/tools; echo y | .\\add-userdic-win.ps1"])# add-userdic-win.ps1와 mecab-ko-dic의 위치로 이동



def save_tags_to_file(tags):
    default_filename = "TextMining.txt"
    image_filename = "result/result.png"

    root = tk.Tk()
    root.withdraw()

    # 파일 대화 상자를 열어 사용자가 파일을 저장할 경로를 선택합니다.
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             initialfile=default_filename,
                                             filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

    if file_path:
        with open(file_path, 'w', encoding='utf-8') as file:
            for tag in tags:
                file.write(f"{tag[0]}: {tag[1]}\n")

    # 결과 이미지 파일 복사
    shutil.copyfile(image_filename, os.path.join(os.path.dirname(file_path), "WordCloud.png"))

    return file_path


# 동적 주소 샘플
# https://blog.naver.com/00eldnjsl/222577148347
# https://blog.naver.com/r3gum/223206650211
# https://blog.naver.com/rkarlcjstk1/223070485507
# https://blog.naver.com/beskilled/223230575253

# ssl 오류 주소 샘플
# https://www.bok.or.kr/portal/bbs/B0000347/view.do?nttId=10080997&menuNo=201106

# bot 방지 주소 샘플
# https://www.hankyung.com/article/2023121216921