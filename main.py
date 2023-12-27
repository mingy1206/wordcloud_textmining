from fastapi import FastAPI
from DataModel import DataModel
from WordCloud import fetch_url_content, generate_wordcloud

app = FastAPI()

@app.post("/wordCloud")
async def receive_data(data: DataModel):
    print(data.font)
    print(data.baseImage)
    print(data.urls)

    all_content = ""  # Initialize a variable to store the combined content

    for url in data.urls:
        content = fetch_url_content(url)
        if content:
            all_content += " " + content  # Concatenate the content

    if all_content:
        output_filename = f"result/result_{data.baseImage}_{data.font}.png"
        generate_wordcloud(all_content, data.font, data.baseImage, output_filename)

    return {"message": "Word cloud generated successfully from all URLs"}

# Rest of your code remains the same