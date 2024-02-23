import numpy as np
import pandas as pd
from wordcloud import WordCloud, ImageColorGenerator
from konlpy.tag import Okt
from collections import Counter

from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
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


def generate_wordcloud(content, font, baseImage, ew,tw):
    pos_tagged = Okt().pos(content)
    noun_adj_list = [word for word, tag in pos_tagged if tag in ['Noun', 'Adjective']]
    print(noun_adj_list)
    exclude_words = ew + ['블로그', '글', '이미지','아이디' '광고', '네이버','이웃','댓글','움','창', '초', '시']
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
        max_words=600
    ).generate_from_frequencies(dict(tags))

    # Use the colors from the mask image for the word cloud
    image_colors = ImageColorGenerator(masking_image)
    wc = wc.recolor(color_func=image_colors)

    # Save to file
    output_filename = "result/result.png"
    wc.to_file(output_filename)

    return {"tags": tags, "image_path": output_filename}


"""

if __name__ == "__main__":
    url = "https://search.naver.com/search.naver?ie=UTF-8&sm=whl_hty&query=%EA%B1%B0%EB%B6%81%EC%84%AC+%EB%A7%9B%EC%A7%91"
    content = fetch_url_content(url)
    if content:
        generate_wordcloud(content, "result/result.png")
"""
# ssl 오류 주소
# https://www.bok.or.kr/portal/bbs/B0000347/view.do?nttId=10080997&menuNo=201106
# bot 방지 주소(success)
# https://www.hankyung.com/article/2023121216921
