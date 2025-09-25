from httpx import Client
import jwt
import time

HELPER_MOBILE_APP_BUNDLE_ID = "com.helperuforstudents.app"
HELPER_PUSH_NOTIFICATION_P8_ID = "VR2VQP2PTT"
PUSH_TOKEN_SECRET = "-----BEGIN PRIVATE KEY-----\nMIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgUC301Q5rejT7yoOm\nZ5hXGBng0jH7E4xBstHYJwZvUpygCgYIKoZIzj0DAQehRANCAAReOJy4lORF++NL\neSqzOygrT+UYWFawUUOzh+WxdEzoS2Txoc+bngfh88vkTRYGEoLRrdWe4LMAmWlp\nmYxeLw7S\n-----END PRIVATE KEY-----".replace(
    "\\n", "\n"
)

TEAM_ID = "735SD6Y6NL"
DEVICE_TOKEN = "5812c06c8c14be0d358bfc1c3d4550a6d5e8d99c586992e0429a97794c2dc92f"

URL = "https://api.sandbox.push.apple.com"

auth_token = jwt.encode(
    {
        "iss": TEAM_ID,
        "iat": int(time.time()),
    },
    PUSH_TOKEN_SECRET,
    algorithm="ES256",
    headers={"alg": "ES256", "kid": HELPER_PUSH_NOTIFICATION_P8_ID},
)


headers = {
    "authorization": f"bearer {auth_token}",
    "apns-topic": HELPER_MOBILE_APP_BUNDLE_ID,
}
payload = {
    "aps": {
        "alert": {
            "title": "New Message",
            "body": "please work",
        }
    }
}


with Client(http2=True) as client:
    response = client.post(
        f"{URL}/3/device/{DEVICE_TOKEN}",
        headers=headers,
        json=payload,
    )

    print(response.read())
