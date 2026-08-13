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
    options.add_argument('--window-size=2560,1440')
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
        
        print("2. Logged in. Moving to site menu...")
        site_menu = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/siteManage/site']"))
        )
        actions = ActionChains(driver)
        actions.move_to_element(site_menu).perform()
        time.sleep(1) 
        
        print("3. Clicking Person List...")
        person_menu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/accessManage/personList']"))
        )
        driver.execute_script("arguments[0].click();", person_menu)
        time.sleep(4) 
        
        print("4. Clicking Customized Tab...")
        customized_tab = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tab-customized"))
        )
        driver.execute_script("arguments[0].click();", customized_tab)
        time.sleep(3)
        
        print("5. Clicking ADD Button (Aggressive Retry Mode)...")
        add_btn_xpath = "//div[@id='pane-customized']//button[.//span[contains(text(), 'Add')]]"
        modal_opened = False
        
        # לולאה שמנסה ללחוץ בכמה שיטות עד שהחלון באמת נפתח
        for attempt in range(4):
            try:
                main_add_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, add_btn_xpath)))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", main_add_btn)
                time.sleep(1)
                
                if attempt == 0:
                    main_add_btn.click() # שיטה 1: לחיצה רגילה
                elif attempt == 1:
                    driver.execute_script("arguments[0].click();", main_add_btn) # שיטה 2: ג'אווה-סקריפט
                elif attempt == 2:
                    main_add_btn.send_keys(Keys.ENTER) # שיטה 3: מקש אנטר
                else:
                    ActionChains(driver).move_to_element(main_add_btn).click().perform() # שיטה 4: עכבר
                
                # בודקים אם החלון נפתח על ידי חיפוש שדה השם
                time.sleep(2)
                if len(driver.find_elements(By.XPATH, "//input[@aria-label='Name']")) > 0:
                    modal_opened = True
                    print(">>> Modal successfully opened! <<<")
                    break
            except Exception as e:
                print(f"Attempt {attempt+1} method failed.")
                
        if not modal_opened:
            raise Exception("CRITICAL ERROR: Failed to open Add Modal! The button refuses to click in Headless.")
        
        # מעכשיו משתמשים רק ב-WebDriverWait קשיח כדי שלא נדלג על כלום בטעות
        print("6. Entering Name...")
        name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Name']"))
        )
        name_input.clear()
        name_input.send_keys(developer_name)
        time.sleep(1)
        
        print("7. Clicking Set PIN...")
        pin_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'setPinBtn')]"))
        )
        driver.execute_script("arguments[0].click();", pin_btn)
        time.sleep(1)
        
        print("8. Checking QR Checkbox...")
        qr_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pin-code-container')]/following-sibling::label//span[contains(@class, 'el-checkbox__inner')]"))
        )
        driver.execute_script("arguments[0].click();", qr_checkbox)
        time.sleep(1)
        
        print("9. Clicking Add Access Rule...")
        access_add_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'secondary') and .//span[contains(text(), 'Add')]]"))
        )
        driver.execute_script("arguments[0].click();", access_add_btn)
        time.sleep(3) 
        
        print("10. Selecting 'יזמים'...")
        yazamim_checkbox = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//tr[.//td[contains(., 'יזמים')]]//span[contains(@class, 'el-checkbox__inner')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", yazamim_checkbox)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", yazamim_checkbox)
        time.sleep(1)
        
        print("11. Clicking OK on Access Rule...")
        ok_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Select from Access Rule']//button[.//span[text()='OK']]"))
        )
        driver.execute_script("arguments[0].click();", ok_button)
        time.sleep(2)
        
        print("12. Saving User...")
        save_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[.//span[contains(text(), 'Save')]]"))
        )
        driver.execute_script("arguments[0].click();", save_button)
        
        time.sleep(6) 
        print(f"Successfully created user: {developer_name}")
        
        print("13. Searching for the new user...")
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Name' or contains(@placeholder, 'Name')]"))
        )
        search_input.clear()
        search_input.send_keys(developer_name)
        time.sleep(1)
        search_input.send_keys(Keys.ENTER)
        time.sleep(4)
        
        print("14. Clicking DETAILS...")
        top_details_btn_xpath = "(//tr[contains(@class, 'el-table__row')][1]//div[@class='btn-item'])[1]"
        details_btn = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, top_details_btn_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", details_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", details_btn)
        
        time.sleep(4) 
        
        print("15. Extracting QR Code...")
        qr_img_xpath = "//div[contains(@class, 'info-value')]//img[contains(@src, 'base64')]"
        qr_img_element = WebDriverWait(driver, 15).until(
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
                print("16. Uploading QR code to Monday.com...")
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
