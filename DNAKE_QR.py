import os
import random
os.environ['WDM_SSL_VERIFY'] = '0'

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import base64
import requests
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def upload_crash_screenshot(driver, item_id, token):
    if not item_id:
        return
    filename = "CRASH_SCREEN.png"
    try:
        driver.save_screenshot(filename)
        upload_url = "https://api.monday.com/v2/file"
        headers = {"Authorization": token}
        query = f'mutation ($file: File!) {{ add_file_to_column (item_id: {item_id}, column_id: "file_mm64npqq", file: $file) {{ id }} }}'
        with open(filename, 'rb') as f:
            files = {'variables[file]': (filename, f, 'image/png')}
            data = {'query': query}
            requests.post(upload_url, headers=headers, data=data, files=files, verify=False)
        print("Crash screenshot uploaded to Monday.")
    except Exception as e:
        print(f"Failed to upload crash screenshot: {e}")

def generate_dnake_qr(developer_name, item_id=None):
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjYyMzIxMjUxOSwiYWFpIjoxMSwidWlkIjo5NzYwMTM1NywiaWFkIjoiMjAyNi0wMi0xOVQwOTowODozMS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjkzNzUzNDYsInJnbiI6ImV1YzEifQ.EsITDIb08RaofyL9eIJae6eFJ_zBUiOBeCugjSMqoDE"
    FILE_COLUMN_ID = "file_mm64npqq"
    
    options = Options()
    options.add_argument('--headless=new') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--ignore-certificate-errors') 
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        output_folder = "."
        
        print(f"1. Starting process for: {developer_name}")
        driver.get("https://eu-cloud.dnake.com/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys("shahar_ro@mail.tel-aviv.gov.il")
        
        driver.find_element(By.NAME, "password").send_keys("Rr304050!")
        driver.find_element(By.CLASS_NAME, "v2-login-button").click()
        
        print("2. Waiting for login to process...")
        site_menu = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/siteManage/site']"))
        )
        time.sleep(2)
        
        print("3. Extracting Security Token from browser...")
        # טריק מטורף: גניבת האסימון המאובטח של השרת היישר מזיכרון הדפדפן!
        auth_token = driver.execute_script("""
            let token = null;
            let vuex = window.localStorage.getItem('vuex');
            if (vuex) {
                try {
                    let v = JSON.parse(vuex);
                    if (v.user && v.user.token) token = v.user.token;
                } catch(e) {}
            }
            if (!token) {
                for (let i = 0; i < window.localStorage.length; i++) {
                    let v = window.localStorage.getItem(window.localStorage.key(i));
                    if (typeof v === 'string' && /^[a-f0-9]{32}$/i.test(v)) token = v;
                }
            }
            return token;
        """)
        
        if not auth_token:
            raise Exception("CRITICAL ERROR: Could not extract authorization token!")
            
        print("Token extracted! Bypassing UI and injecting user via API...")
        
        # ==========================================
        # פצצת האטום: יצירת משתמש ישירות ב-API
        # ==========================================
        api_url = "https://eu-api-cloud.ss-iot.com/admin-api/business/ac-person/v1/create"
        
        # בניית PIN קוד אקראי בן 8 ספרות
        random_pin = str(random.randint(10000000, 99999999))
        
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en_US',
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://eu-cloud.dnake.com',
            'Project-Id': '2051211421803474944',
            'Role-Type': '14',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        
        payload = {
            "name": developer_name,
            "remark": "",
            "email": "",
            "qrcodeEnable": True,
            "acGroupList": [{"groupId": "2056761567895093250"}], # הקבוצה של היזמים
            "role": 7,
            "uploadStr": "",
            "facePhoto": "",
            "fileId": "",
            "icCardReqVOList": [],
            "pinCode": random_pin
        }
        
        response = requests.post(api_url, json=payload, headers=headers, verify=False)
        print(f"API Response: {response.text}")
        
        if response.status_code == 200:
            print(">>> User created flawlessly via API! <<<")
        else:
            print("API returned an error, but continuing to UI just in case...")

        # ==========================================
        # חזרה לממשק הרגיל רק כדי להוריד את התמונה
        # ==========================================
        print("4. Opening Person List...")
        person_menu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/accessManage/personList']"))
        )
        driver.execute_script("arguments[0].click();", person_menu)
        time.sleep(3) 
        
        print("5. Clicking Customized Tab...")
        customized_tab = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tab-customized"))
        )
        driver.execute_script("arguments[0].click();", customized_tab)
        time.sleep(3)
        
        print("6. Searching for the new user...")
        search_inputs = driver.find_elements(By.XPATH, "//input[@aria-label='Name' or contains(@placeholder, 'Name')]")
        for inp in search_inputs:
            if inp.is_displayed():
                inp.clear()
                inp.send_keys(developer_name)
                time.sleep(1)
                inp.send_keys(Keys.ENTER)
                break
        time.sleep(3)
        
        print("7. Clicking DETAILS...")
        top_details_btn_xpath = "(//tr[contains(@class, 'el-table__row')][1]//div[@class='btn-item'])[1]"
        details_btn = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, top_details_btn_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", details_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", details_btn)
        
        time.sleep(3) 
        
        print("8. Extracting QR Code...")
        qr_img_xpath = "//div[contains(@class, 'info-value')]//img[contains(@src, 'base64')]"
        qr_img_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, qr_img_xpath))
        )
        
        base64_data = qr_img_element.get_attribute("src")
        
        if "base64," in base64_data:
            base64_string = base64_data.split("base64,")[1]
            img_data = base64.b64decode(base64_string)
            
            file_name = f"qr_{item_id}.png" if item_id else f"qr_{developer_name}.png"
            file_path = os.path.join(output_folder, file_name)
            
            with open(file_path, "wb") as f:
                f.write(img_data)
                
            print(f"BINGO! QR code saved successfully as: {file_path}")
            
            if item_id:
                print("9. Uploading QR code to Monday.com...")
                upload_url = "https://api.monday.com/v2/file"
                headers = {"Authorization": MONDAY_API_TOKEN}
                
                query = f'mutation ($file: File!) {{ add_file_to_column (item_id: {item_id}, column_id: "{FILE_COLUMN_ID}", file: $file) {{ id }} }}'
                
                with open(file_path, 'rb') as f:
                    files = {'variables[file]': (os.path.basename(file_path), f, 'image/png')}
                    data = {'query': query}
                    response = requests.post(upload_url, headers=headers, data=data, files=files, verify=False)
                
                if response.status_code == 200 and 'errors' not in response.json():
                    print("Success: File uploaded to Monday perfectly!")
                else:
                    print(f"Failed to upload to Monday: {response.text}")

            return file_path
        else:
            print("Error: Could not find base64 image data.")
            return None

    except Exception as e:
        print("--- ERROR TRACEBACK ---")
        traceback.print_exc()
        print(f"An error occurred: {e}")
        upload_crash_screenshot(driver, item_id, MONDAY_API_TOKEN)
        return None
        
    finally:
        driver.quit()
