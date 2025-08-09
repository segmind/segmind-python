from dotenv import load_dotenv

from segmind.client import SegmindClient

load_dotenv()

client = SegmindClient()

response = client.run(
    "seedream-v3-text-to-image",
    prompt="A beautiful raining sunrise over dark icy mountains",
    aspect_ratio="16:9",
)


with open("sunrise.jpg", "wb") as f:
    f.write(response.content)
