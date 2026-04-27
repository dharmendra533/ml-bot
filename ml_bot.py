import requests, time
from sklearn.linear_model import LogisticRegression

TOKEN = "8634693972:AAGS0sUVgHnE2qdReUOIEmorM7C7tlllz-g"
CHAT_ID = "1002304843811"

last_period = ""

def get_data():
    url = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
    data = requests.get(url, timeout=10).json()
    nums = [int(x["number"]) for x in data["data"]["list"][:60]]
    period = data["data"]["list"][0]["issue"]
    return nums, period

def create_dataset(nums):
    X, y = [], []
    for i in range(len(nums)-5):
        window = nums[i:i+5]
        target = nums[i+5]
        X.append([1 if n>=5 else 0 for n in window])
        y.append(1 if target>=5 else 0)
    return X, y

def predict(nums):
    X, y = create_dataset(nums)
    model = LogisticRegression(max_iter=200)
    model.fit(X, y)

    last = nums[:5]
    features = [[1 if n>=5 else 0 for n in last]]
    prob = model.predict_proba(features)[0]

    if prob[1] > prob[0]:
        return "BIG", prob[1]
    else:
        return "SMALL", prob[0]

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

while True:
    try:
        nums, period = get_data()
        if period != last_period:
            res, conf = predict(nums)
            conf = round(conf*100, 2)

            if conf >= 60:  # filter
                msg = f"""🤖 SERVER ML

Period: {period}
Prediction: {res}
Confidence: {conf}%"""
                send(msg)
                print("Sent:", period, res, conf)
            else:
                print("Skip:", conf)

            last_period = period

    except Exception as e:
        print("Error:", e)

    time.sleep(60)