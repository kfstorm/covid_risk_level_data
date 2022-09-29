import json
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


service = Service(executable_path=ChromeDriverManager().install())
capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
options = ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")

def get_target_log(driver):
    print(driver.title)
    logs = driver.get_log("performance")
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
            "Network.responseReceived" == log["method"]
            and "interfaceJson" in log["params"]["response"]["url"]
        ):
            return log


def parse_response(log):
    print(json.dumps(log, indent=2))
    body = json.loads(driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': log["params"]["requestId"]})["body"])
    code = body["code"]
    msg = body["msg"]
    if code != 0:
        raise Exception(f"Bad data. code: {code}. msg: {msg}")
    data = body["data"]
    normalize_data(data)
    with open("data.json", "w") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))


def normalize_data(data):
    """Sort lists for easier diffing"""
    def sort_list(risk_list):
        risk_list.sort(key=lambda x: (x["province"], x["city"], x["county"], x["area_name"]))
        for item in risk_list:
            item["communitys"].sort()

    sort_list(data["highlist"])
    sort_list(data["middlelist"])
    sort_list(data["lowlist"])


with webdriver.Chrome(service=service, desired_capabilities=capabilities, options=options) as driver:
    driver.get("http://bmfw.www.gov.cn/yqfxdjcx/risk.html")
    start_time = time.time()
    log = None
    while time.time() - start_time < 60:
        try:
            log = get_target_log(driver)
            if log:
                break
        except Exception as e:
            print(e)
            time.sleep(1)
    else:
        raise TimeoutError()
    parse_response(log)
