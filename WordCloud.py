import os
from collections import Counter
from konlpy.tag import Mecab

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
    all_content = ""
    for url in urls:
        content = fetch_url_content_selenium(url)  # 앞서 정의한 함수 사용
        if content:
            all_content += " " + content  # 콘텐츠를 모두 합침
    return all_content

def fetch_url_content_selenium(url):
    # Set up Chrome options for Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no browser UI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    print(1)
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    content = ""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # 메인 페이지의 콘텐츠 가져오기
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
                # 오류가 발생해도 다음 iframe으로 계속 진행

        return content
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        driver.quit()


def generate_wordcloud(content, font, baseImage, ew, tw):
    print(tw)
    tword = []
    for check in tw:
        if check != '':
            tword.append(check)
        print("if")
        print(tword)
        print(len(tword))
        train_word(tword)

    else :
        print("else")
        print(tw)
        print(len(tw))

    pos_tagged = Mecab("venv/Lib/site-packages/mecab/tools/mecab-ko-dic").pos(content)
    print("-------------------content--------------------------")
    print(content)
    print("------------------pos_tagged--------------------------")
    print(pos_tagged)
    print("------------------noun_adj_list--------------------------")
    noun_adj_list = [word for word, tag in pos_tagged if tag in ['NNG', 'SL', 'NNP', 'VA+ETM', 'SH']]
    print(noun_adj_list)
    print("------------------finish--------------------------")
    exclude_words = ew + ['블로그', '글', '이미지','아이디','검색', '광고', '네이버','이웃','댓글','움','창', '초', '시']
    k_stopword = pd.read_csv('korean_stopword.csv')
    k_stopword = list(k_stopword['불용어'])
    exclude_words = exclude_words +k_stopword


    filtered_words = [word for word in noun_adj_list if word not in exclude_words]

    counts = Counter(filtered_words)
    tags = counts.most_common(1000)

    masking_image = np.array(Image.open("images/{}.png".format(baseImage)))
    print(tags)

    # Create a word cloud instance with mask
    wc = WordCloud(
        font_path="font/{}/{}.otf".format(font, font),
        mask=masking_image,
        background_color='white',
        max_font_size=300,
        min_font_size=1,
        max_words=1000
    ).generate_from_frequencies(dict(tags))

    # Use the colors from the mask image for the word cloud
    image_colors = ImageColorGenerator(masking_image)
    wc = wc.recolor(color_func=image_colors)

    # Save to file
    output_filename = "result/result.png"
    wc.to_file(output_filename)

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

    os.system('cd venv/Lib/site-packages/mecab/tools')
    os.system('.\add-userdic-win.ps1')




# ssl 오류 주소
# https://www.bok.or.kr/portal/bbs/B0000347/view.do?nttId=10080997&menuNo=201106
# bot 방지 주소(success)
# https://www.hankyung.com/article/2023121216921
