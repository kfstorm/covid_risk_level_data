import json
import time

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


service = Service(executable_path=ChromeDriverManager().install())
capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

def get_target_log(driver):
    logs = driver.get_log("performance")
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
            "Network.responseReceived" == log["method"]
            and "interfaceJson" in log["params"]["response"]["url"]
        ):
            return log

def parse_response(log):
    body = json.loads(driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': log["params"]["requestId"]})["body"])
    code = body["code"]
    msg = body["msg"]
    if code != 0:
        raise Exception(f"Bad data. code: {code}. msg: {msg}")
    data = body["data"]
    with open("data.json", "w") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))


with webdriver.Chrome(service=service, desired_capabilities=capabilities) as driver:
    driver.get("http://bmfw.www.gov.cn/yqfxdjcx/risk.html")
    start_time = time.time()
    log = None
    while time.time() - start_time < 60:
        try:
            log = get_target_log(driver)
            break
        except Exception as e:
            print(e)
            time.sleep(1)
    else:
        raise TimeoutError()
    parse_response(log)
