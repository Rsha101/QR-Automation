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

def upload_step_screenshot(driver, step_name, item_id, token):
    if not item_id:
        return
    filename = f"{step_name}.png"
    try:
        driver.save_screenshot(filename)
        upload_url = "https://api.monday.com/v2/file"
        headers = {"Authorization": token}
        query = f'mutation ($file: File!) {{ add_file_to_column (item_id: {item_id}, column_id: "file_mm64npqq", file: $file) {{ id }} }}'
        
        with open(filename, 'rb') as f:
            files = {'variables[file]': (filename, f, 'image/png')}
            data = {'query': query}
            requests.post(upload_url, headers=headers, data=data, files=files, verify=False)
        print(f"DEBUG STEP: Screenshot '{step_name}' uploaded to Monday.")
    except Exception as e:
        print(f"Failed to upload step screenshot {step_name}: {e}")

def generate_dnake_qr(developer_name, item_id=None):
    MONDAY_API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjYyMzIxMjUxOSwiYWFpIjoxMSwidWlkIjo5NzYwMTM1NywiaWFkIjoiMjAyNi0wMi0xOVQwOTowODozMS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjkzNzUzNDYsInJnbiI6ImV1YzEifQ.EsITDIb08RaofyL9eIJae6eFJ_zBUiOBeCugjSMqoDE"
    FILE_COLUMN_ID = "file_mm64npqq"
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=2560,1440')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--lang=en-US') 
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print(f"Starting process for: {developer_name}")
        driver.get("https://eu-cloud.dnake.com/login")
        
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("shahar_ro@mail.tel-aviv.gov.il")
        driver.find_element(By.NAME, "password").send_keys("Rr304050!")
        driver.find_element(By.CLASS_NAME, "v2-login-button").click()
        
        print("Logged in, navigating to Person List...")
        upload_step_screenshot(driver, "step_1_logged_in", item_id, MONDAY_API_TOKEN)
        
        site_menu = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/siteManage/site']")))
        ActionChains(driver).move_to_element(site_menu).perform()
        time.sleep(2) 
        
        person_menu = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/accessManage/personList']")))
        driver.execute_script("arguments[0].click();", person_menu)
        time.sleep(5)
        upload_step_screenshot(driver, "step_2_person_list", item_id, MONDAY_API_TOKEN)
        
        print("Clicking Customized tab...")
        customized_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "tab-customized")))
        driver.execute_script("arguments[0].click();", customized_tab)
        time.sleep(3)
        upload_step_screenshot(driver, "step_3_customized_tab", item_id, MONDAY_API_TOKEN)
        
        print("Forcing Add button click with MouseEvent simulation...")
        add_btn_xpath = "//div[@id='pane-customized']//button[.//span[contains(text(), 'Add')]]"
        main_add_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, add_btn_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", main_add_btn)
        time.sleep(1)
        
        # לחיצה אגרסיבית שמדמה פעולה אנושית מלאה
        driver.execute_script("""
            var el = arguments[0];
            el.focus();
            ['mouseover', 'mousedown', 'mouseup', 'click'].forEach(function(e) {
                var ev = document.createEvent('MouseEvent');
                ev.initMouseEvent(e, true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                el.dispatchEvent(ev);
            });
        """, main_add_btn)
            
        print("Waiting for modal to open...")
        # וידוא קשיח: המתנה עד ששדה השם בחלון הקופץ אכן יופיע במסך!
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Name']"))
        )
        upload_step_screenshot(driver, "step_4_modal_opened", item_id, MONDAY_API_TOKEN)
        
        print("Entering name natively...")
        name_inputs = driver.find_elements(By.XPATH, "//input[@aria-label='Name']")
        for inp in name_inputs:
            if inp.is_displayed():
                inp.click()
                time.sleep(0.5)
                inp.clear()
                time.sleep(0.5)
                inp.send_keys(developer_name)
                time.sleep(0.5)
                inp.send_keys(Keys.TAB)
                break
        time.sleep(1)
        upload_step_screenshot(driver, "step_5_name_entered", item_id, MONDAY_API_TOKEN)
        
        print("Clicking setPinBtn...")
        pin_btns = driver.find_elements(By.XPATH, "//button[contains(@class, 'setPinBtn')]")
        for btn in pin_btns:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
        time.sleep(2)
        upload_step_screenshot(driver, "step_6_pin_clicked", item_id, MONDAY_API_TOKEN)
        
        print("Checking QR Checkbox...")
        qr_checkboxes = driver.find_elements(By.XPATH, "//div[contains(@class, 'pin-code-container')]/following-sibling::label//span[contains(@class, 'el-checkbox__inner')]")
        for cb in qr_checkboxes:
            if cb.is_displayed():
                driver.execute_script("arguments[0].click();", cb)
                break
        time.sleep(1)
        upload_step_screenshot(driver, "step_7_qr_checked", item_id, MONDAY_API_TOKEN)
        
        print("Adding Access Rule...")
        access_add_btns = driver.find_elements(By.XPATH, "//button[contains(@class, 'secondary') and .//span[contains(text(), 'Add')]]")
        for btn in access_add_btns:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
                
        time.sleep(4) 
        upload_step_screenshot(driver, "step_8_access_modal_opened", item_id, MONDAY_API_TOKEN)
        
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
        upload_step_screenshot(driver, "step_9_yazamim_selected", item_id, MONDAY_API_TOKEN)
        
        print("Clicking OK for access rule...")
        ok_buttons = driver.find_elements(By.XPATH, "//div[@aria-label='Select from Access Rule']//button[.//span[text()='OK']]")
        for btn in ok_buttons:
            if btn.is_displayed():
                driver.execute_script("arguments[0].click();", btn)
                break
                
        time.sleep(5) 
        upload_step_screenshot(driver, "step_10_access_rule_ok", item_id, MONDAY_API_TOKEN)
        
        print("Saving User...")
        save_buttons = driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'Save')]]")
        clicked_save_btn = None
        
        for btn in save_buttons:
            if btn.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", btn)
                clicked_save_btn = btn
                break
        
        if not clicked_save_btn:
            raise Exception("CRITICAL ERROR: Save button was not found or is hidden!")
            
        time.sleep(6) 
        upload_step_screenshot(driver, "step_11_after_save", item_id, MONDAY_API_TOKEN)
        
        print(">>> VERIFICATION STEP: Checking if user was actually created! <<<")
        search_inputs = driver.find_elements(By.XPATH, "//input[@aria-label='Name' or contains(@placeholder, 'Name')]")
        for inp in search_inputs:
            if inp.is_displayed():
                inp.clear()
                inp.send_keys(developer_name)
                time.sleep(1)
                inp.send_keys(Keys.ENTER)
                break
                
        time.sleep(4) 
        upload_step_screenshot(driver, "step_12_search_verification", item_id, MONDAY_API_TOKEN)
        
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, f"//td[contains(., '{developer_name}')]")))
            print(f"BINGO: User '{developer_name}' verified in table!")
        except:
            raise Exception(f"CRITICAL ERROR: User '{developer_name}' was NOT created.")
        
        print("Clicking topmost DETAILS button of the verified result...")
        top_details_btn_xpath = "(//tr[contains(@class, 'el-table__row')][1]//div[@class='btn-item'])[1]"
        details_btn = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, top_details_btn_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", details_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", details_btn)
        
        time.sleep(4) 
        upload_step_screenshot(driver, "step_13_details_opened", item_id, MONDAY_API_TOKEN)
        
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
                print("Uploading final QR code to Monday.com...")
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
        error_msg = str(e)
        print(f"Error Message: {error_msg}")
        upload_step_screenshot(driver, "Z_CRASH_ERROR_SCREEN", item_id, MONDAY_API_TOKEN)
        return None
        
    finally:
        driver.quit()
