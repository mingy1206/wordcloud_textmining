import numpy as np
from matplotlib import pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
from konlpy.tag import Okt
from collections import Counter
import pycurl
from io import BytesIO
from PIL import Image


# If needed, import BeautifulSoup from bs4

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

    return buffer.getvalue().decode('utf-8')


def generate_wordcloud(text, font, baseImage, output_filename):
    twitter = Okt()
    pos_tagged = twitter.pos(text)

    # noun_adj_list = [word for word, tag in pos_tagged if tag in ['Noun', 'Adjective']]
    noun_adj_list = [word for word, tag in pos_tagged if tag in ['Noun', 'Adjective']]

    exclude_words = ['입니다', '의', '이', '창']
    noun_adj_list = [word for word in noun_adj_list if word not in exclude_words]

    print(noun_adj_list)
    counts = Counter(noun_adj_list)
    tags = counts.most_common(600)

    masking_image = np.array(Image.open("images/{}.png".format(baseImage)))

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
    wc.to_file(output_filename)


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
