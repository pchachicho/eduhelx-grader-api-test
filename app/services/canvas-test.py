from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# Assuming you have stored your Canvas LMS API key securely
CANVAS_API_KEY = "7006~RMJbYVaRDn3SeKt3kekSHJ1RaVk5oLbmDjkxg650f2rQ6MXwHoeAl3xiWO2rtnzZ"
CANVAS_API_URL = "https://uncch.instructure.com/api/v1"

headers = {
    "Authorization": f"Bearer {CANVAS_API_KEY}"
}

url = f"{CANVAS_API_URL}/accounts"

response = requests.get(url, headers=headers)
print(response.json())


# Test the Assignment API

url = f"{CANVAS_API_URL}/courses/1/assignments"

response = requests.get(url, headers=headers);



