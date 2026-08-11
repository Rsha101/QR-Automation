import os
# חובה לשים את השורה הזו לפני הייבוא של סלניום כדי לעקוף את חסימת ה-SSL של העבודה
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

# העלמת אזהרות אבטחה שיופיעו בגלל ביטול ה-SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_dnake_qr(developer_name, item_id=None):
    # ==========================================
    # הגדרות מאנדיי
    # ==========================================
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjYyMzIxMjUxOSwiYWFpIjoxMSwidWlkIjo5NzYwMTM1NywiaWFkIjoiMjAyNi0wMi0xOVQwOTowODozMS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjkzNzUzNDYsInJnbiI6ImV1YzEifQ.EsITDIb08RaofyL9eIJae6eFJ_zBUiOBeCugjSMqoDE"
    FILE_COLUMN_ID = "file_mm64npqq"
    
    # ==========================================
    # הגדרות כרום (מצב Headless ועקיפת חסימות)
    # ==========================================
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--ignore-certificate-errors') # התעלמות משגיאות SSL בדפדפן עצמו
    
    # עקיפת ה-SSL בהורדת הדרייבר
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        output_folder = "קודים"
        os.makedirs(output_folder, exist_ok=True)
        
        driver.get("https://eu-cloud.dnake.com/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        ).send_keys("shahar_ro@mail.tel-aviv.gov.il")
        
        driver.find_element(By.NAME, "password").send_keys("Rr304050!")
        driver.find_element(By.CLASS_NAME, "v2-login-button").click()
        
        site_menu = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/siteManage/site']"))
        )
        actions = ActionChains(driver)
        actions.move_to_element(site_menu).perform()
        time.sleep(1) 
        
        person_menu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@href='/accessManage/personList']"))
        )
        driver.execute_script("arguments[0].click();", person_menu)
        time.sleep(3) 
        
        customized_tab = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tab-customized"))
        )
        driver.execute_script("arguments[0].click();", customized_tab)
        time.sleep(2)
        
        main_add_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='pane-customized']//button[.//span[contains(text(), 'Add')]]"))
        )
        main_add_btn.click() 
        time.sleep(2)
        
        name_inputs = driver.find_elements(By.XPATH, "//input[@aria-label='Name']")
        for inp in name_inputs:
            if inp.is_displayed():
                inp.send_keys(developer_name)
                break
        time.sleep(1)
        
        pin_btns = driver.find_elements(By.XPATH, "//button[contains(@class, 'setPinBtn')]")
        for btn in pin_btns:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
        time.sleep(1)
        
        qr_checkboxes = driver.find_elements(By.XPATH, "//div[contains(@class, 'pin-code-container')]/following-sibling::label//span[contains(@class, 'el-checkbox__inner')]")
        for cb in qr_checkboxes:
            if cb.is_displayed():
                driver.execute_script("arguments[0].click();", cb)
                break
        time.sleep(1)
        
        access_add_btns = driver.find_elements(By.XPATH, "//button[contains(@class, 'secondary') and .//span[contains(text(), 'Add')]]")
        for btn in access_add_btns:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
        time.sleep(2) 
        
        yazamim_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//tr[.//td[contains(., 'יזמים')]]//span[contains(@class, 'el-checkbox__inner')]"))
        )
        driver.execute_script("arguments[0].click();", yazamim_checkbox)
        time.sleep(1)
        
        ok_buttons = driver.find_elements(By.XPATH, "//div[@aria-label='Select from Access Rule']//button[.//span[text()='OK']]")
        for btn in ok_buttons:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
        time.sleep(2)
        
        save_buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'Save')]]")
        for btn in save_buttons:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
        
        time.sleep(6) 
        print(f"Successfully created user: {developer_name}")
        
        top_details_btn_xpath = "(//tr[contains(@class, 'el-table__row')][1]//div[@class='btn-item'])[1]"
        details_btn = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, top_details_btn_xpath))
        )
        
        driver.execute_script("arguments[0].scrollIntoView(true);", details_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", details_btn)
        print("Successfully clicked on the topmost DETAILS button.")
        
        time.sleep(3) 
        
        qr_img_xpath = "//div[contains(@class, 'info-value')]//img[contains(@src, 'base64')]"
        qr_img_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, qr_img_xpath))
        )
        
        base64_data = qr_img_element.get_attribute("src")
        
        if "base64," in base64_data:
            base64_string = base64_data.split("base64,")[1]
            img_data = base64.b64decode(base64_string)
            
            file_path = os.path.join(output_folder, f"qr_{developer_name}.png")
            with open(file_path, "wb") as f:
                f.write(img_data)
                
            print(f"BINGO! QR code saved successfully as: {file_path}")
            
            # ==========================================
            # העלאת הקובץ ישירות למאנדיי (גרסה מתוקנת)
            # ==========================================
            if item_id:
                print("Uploading QR code to Monday.com...")
                upload_url = "https://api.monday.com/v2/file"
                
                # המפתח כאן הוא להשתמש ב-query ו-map בצורה שמאנדיי אוהב
                query = "mutation ($file: File!) { add_file_to_column (item_id: " + str(item_id) + ', column_id: "' + FILE_COLUMN_ID + '", file: $file) { id } }'
                
                with open(file_path, 'rb') as f:
                    files = {
                        'query': (None, query),
                        'variables[file]': (os.path.basename(file_path), f, 'image/png')
                    }
                    headers = {"Authorization": MONDAY_API_TOKEN}
                    response = requests.post(upload_url, headers=headers, files=files, verify=False)
                
                print(f"Monday Response Status: {response.status_code}")
                print(f"Monday Response Text: {response.text}")
                
                if response.status_code == 200:
                    print("Success: File uploaded to Monday perfectly!")
                else:
                    print(f"Failed to upload to Monday: {response.text}")

            return file_path
        else:
            print("Error: Could not find base64 image data.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        
    finally:
        driver.quit()

