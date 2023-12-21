from fastapi import FastAPI

from DataModel import DataModel
from WordCloud import fetch_url_content, generate_wordcloud

# Import other necessary modules...

app = FastAPI()


@app.post("/wordCloud")
async def receive_data(data: DataModel):
    print(data.font)
    print(data.baseImage)
    print(data.urls)

    for url in data.urls:
        content = fetch_url_content(url)
        if content:
            output_filename = f"result/result_{data.baseImage}_{data.font}.png"
            generate_wordcloud(content, data.font, data.baseImage, output_filename)
    return {"message": "Word clouds generated successfully for all URLs"}
