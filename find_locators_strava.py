import selenium
print("Selenium is working in this environment!")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Safari()
driver.get('https://www.strava.com/login')
wait = WebDriverWait(driver, 10)

# 1) Wait for *any* input to appear in the DOM
wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))

# 2) Grab them all and print their HTML and key attributes
input_elements = driver.find_elements(By.TAG_NAME, "input")
for idx in range(len(input_elements)):
    try:
        # Re-fetch the input element inside the loop
        inp = driver.find_elements(By.TAG_NAME, "input")[idx]
        print(f"Input #{idx}")
        print("  id:    ", inp.get_attribute("id"))
        print("  name:  ", inp.get_attribute("name"))
        print("  outer:", inp.get_attribute("outerHTML"))
        print("---")
    except Exception as e:
        print(f"  ⚠️ Skipped Input #{idx} due to error: {e}")

