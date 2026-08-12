import os
os.environ['WDM_SSL_VERIFY'] = '0'

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import base64
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_dnake_qr(developer_name, item_id=None):
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjYyMzIxMjUxOSwiYWFpIjoxMSwidWlkIjo5NzYwMTM1NywiaWFkIjoiMjAyNi0wMi0xOVQwOTowODozMS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjkzNzUzNDYsInJnbiI6ImV1YzEifQ.EsITDIb08RaofyL9eIJae6eFJ_zBUiOBeCugjSMqoDE"
    FILE_COLUMN_ID = "file_mm64npqq"
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # הגדלת הרזולוציה למקסימום כדי ששום אלמנט לא יברח מהמסך
    options.add_argument('--window-size=2560,1440')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print(f"Starting process for: {developer_name}")
        driver.get("https://eu-cloud.dnake.com/login")
        
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("shahar_ro@mail.tel-aviv.gov.il")
        driver.find_element(By.NAME, "password").send_keys("Rr304050!")
        driver.find_element(By.CLASS_NAME, "v2-login-button").click()
        
        print("Logged in, navigating to Person List...")
        site_menu = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/siteManage/site']")))
        ActionChains(driver).move_to_element(site_menu).perform()
        time.sleep(2) 
        
        person_menu = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/accessManage/personList']")))
        driver.execute_script("arguments[0].click();", person_menu)
        time.sleep(5)
        
        print("Clicking Customized tab...")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "tab-customized"))).click()
        time.sleep(3)
        
        print("Clicking Add button...")
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='pane-customized']//button[.//span[contains(text(), 'Add')]]"))).click()
        
        print("Waiting for name input field...")
        time.sleep(3) 
        name_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Name') or @aria-label='Name']"))
        )
        driver.execute_script("arguments[0].value = '';", name_input)
        driver.execute_script(f"arguments[0].value = '{developer_name}';", name_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", name_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", name_input)
        
        # --- גלילה אל הכפתור ולחיצה בטוחה ---
        print("Scrolling to and clicking setPinBtn...")
        time.sleep(2)
        pin_btn = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "setPinBtn"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", pin_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", pin_btn)
        # ------------------------------------
        
        driver.find_element(By.XPATH, "//div[contains(@class, 'pin-code-container')]/following-sibling::label//span[contains(@class, 'el-checkbox__inner')]").click()
        
        driver.find_elements(By.XPATH, "//button[contains(., 'Add')]")[-1].click()
        time.sleep(2)
        driver.find_element(By.XPATH, "//tr[.//td[contains(., 'יזמים')]]//span[contains(@class, 'el-checkbox__inner')]").click()
        driver.find_elements(By.XPATH, "//button[.//span[text()='OK']]")[-1].click()
        time.sleep(2)
        
        # כפתור ה-SAVE
        print("Clicking Save button...")
        save_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'primarybutton') and .//span[text()='Save']]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
        driver.execute_script("arguments[0].click();", save_btn)
        
        print("User saved, waiting for table refresh...")
        time.sleep(8)
        
        driver.find_elements(By.CLASS_NAME, "btn-item")[0].click()
        time.sleep(4)
        
        qr_img = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'info-value')]//img[contains(@src, 'base64')]")))
        base64_data = qr_img.get_attribute("src").split("base64,")[1]
        
        file_path = f"qr_{item_id}.png"
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(base64_data))
        print("QR saved locally.")
        
        if item_id:
            print("Uploading to Monday...")
            upload_url = "https://api.monday.com/v2/file"
            query = f'mutation ($file: File!) {{ add_file_to_column (item_id: {item_id}, column_id: "{FILE_COLUMN_ID}", file: $file) {{ id }} }}'
            with open(file_path, 'rb') as f:
                files = {'query': (None, query), 'variables[file]': (file_path, f, 'image/png')}
                resp = requests.post(upload_url, headers={"Authorization": MONDAY_API_TOKEN}, files=files, verify=False)
                print(f"Monday API status: {resp.status_code}, Response: {resp.text}")
                
        return file_path

    except Exception as e:
        print(f"ERROR: {e}")
        return None
    finally:
        driver.quit()
