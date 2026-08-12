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

def generate_dnake_qr(developer_name, item_id=None):
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjYyMzIxMjUxOSwiYWFpIjoxMSwidWlkIjo5NzYwMTM1NywiaWFkIjoiMjAyNi0wMi0xOVQwOTowODozMS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjkzNzUzNDYsInJnbiI6ImV1YzEifQ.EsITDIb08RaofyL9eIJae6eFJ_zBUiOBeCugjSMqoDE"
    FILE_COLUMN_ID = "file_mm64npqq"
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=2560,1440')
    options.add_argument('--ignore-certificate-errors')
    
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
        customized_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tab-customized")))
        driver.execute_script("arguments[0].click();", customized_tab)
        time.sleep(3)
        
        print("Clicking Add button...")
        main_add_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='pane-customized']//button[.//span[contains(text(), 'Add')]]"))
        )
        main_add_btn.click() 
        time.sleep(3)
        
        print("Entering name...")
        name_inputs = driver.find_elements(By.XPATH, "//input[@aria-label='Name']")
        for inp in name_inputs:
            if inp.is_displayed():
                inp.click() # לחיצה על השדה כדי למקד אותו
                inp.clear()
                inp.send_keys(developer_name)
                time.sleep(0.5)
                inp.send_keys(Keys.TAB) # הדמיית יציאה מהשדה כדי שהאתר יקלוט את הטקסט!
                break
        time.sleep(1)
        
        print("Clicking setPinBtn...")
        pin_btns = driver.find_elements(By.XPATH, "//button[contains(@class, 'setPinBtn')]")
        for btn in pin_btns:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
        time.sleep(2)
        
        print("Checking QR Checkbox...")
        qr_checkboxes = driver.find_elements(By.XPATH, "//div[contains(@class, 'pin-code-container')]/following-sibling::label//span[contains(@class, 'el-checkbox__inner')]")
        for cb in qr_checkboxes:
            if cb.is_displayed():
                driver.execute_script("arguments[0].click();", cb)
                break
        time.sleep(1)
        
        print("Adding Access Rule...")
        access_add_btns = driver.find_elements(By.XPATH, "//button[contains(@class, 'secondary') and .//span[contains(text(), 'Add')]]")
        for btn in access_add_btns:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
                
        time.sleep(4) 
        
        print("Selecting 'יזמים'...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//tr[.//td[contains(., 'יזמים')]]"))
        )
        
        yazamim_checkboxes = driver.find_elements(By.XPATH, "//tr[.//td[contains(., 'יזמים')]]//span[contains(@class, 'el-checkbox__inner')]")
        for cb in yazamim_checkboxes:
            if cb.is_displayed():
                driver.execute_script("arguments[0].click();", cb)
                break
        time.sleep(1)
        
        print("Clicking OK for access rule...")
        ok_buttons = driver.find_elements(By.XPATH, "//div[@aria-label='Select from Access Rule']//button[.//span[text()='OK']]")
        for btn in ok_buttons:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
                
        time.sleep(3) 
        
        print("Saving User...")
        save_buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'Save')]]")
        clicked_save_btn = None
        
        for btn in save_buttons:
            if btn.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(1)
                # שימוש ב-ActionChains ללחיצה הכי טבעית שיש
                ActionChains(driver).move_to_element(btn).click().perform()
                clicked_save_btn = btn
                break
        
        print("Waiting for modal to close (confirming save)...")
        # הוידוא הקריטי: אנחנו עוצרים את הקוד ולא ממשיכים עד שכפתור השמירה נעלם!
        if clicked_save_btn:
            WebDriverWait(driver, 20).until(EC.invisibility_of_element(clicked_save_btn))
            
        print("User saved successfully, waiting for table refresh...")
        time.sleep(5) 
        
        print("Clicking topmost DETAILS button...")
        top_details_btn_xpath = "(//tr[contains(@class, 'el-table__row')][1]//div[@class='btn-item'])[1]"
        details_btn = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, top_details_btn_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", details_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", details_btn)
        
        time.sleep(4) 
        
        print("Extracting QR Image...")
        qr_img_xpath = "//div[contains(@class, 'info-value')]//img[contains(@src, 'base64')]"
        qr_img_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, qr_img_xpath))
        )
        
        base64_data = qr_img_element.get_attribute("src")
        file_path = f"qr_{item_id}.png"
        
        if "base64," in base64_data:
            base64_string = base64_data.split("base64,")[1]
            img_data = base64.b64decode(base64_string)
            
            with open(file_path, "wb") as f:
                f.write(img_data)
                
            print(f"QR code saved successfully!")
            
            if item_id:
                print("Uploading QR code to Monday.com...")
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
        return None
        
    finally:
        driver.quit()
