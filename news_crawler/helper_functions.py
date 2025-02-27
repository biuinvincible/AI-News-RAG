import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def login_facebook(username, password, driver):
    '''Log in to Facebook'''

    try:
        # Wait 10s until the login form is loaded
        username_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "email")))
        username_field.send_keys(username)

        password_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "pass")))
        password_field.send_keys(password)

        # Submit log in form 
        password_field.send_keys(Keys.RETURN)

    except Exception as e:
        print("Logged in failed. \n")

    finally:
        print("Logged in successfully")

def configure_driver():
    '''Configure the webdriver'''

    #Configurations
    webdriver_path = os.path.join(os.path.dirname(__file__), "chromedriver") #your webdriver path (chromedriver.exe)

    chrome_options = Options()

    # Turn off Chrome notification and set language to English
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--disable-notifications")
    chrome_options.set_capability('pageLoadStrategy', 'none')  # Hoặc 'eager'
    # chrome_options.add_argument("--enable-features=Translate")
    # chrome_options.add_argument("--force-translate-en")  # Ép dịch sang tiếng Anh
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--disable-features=ScriptStreaming")  # Chặn request nền
    chrome_options.add_argument("--disable-features=PreloadMediaEngagementData")  # Chặn preload
    chrome_options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,  # 2 = Block
        "profile.managed_default_content_settings.videos": 2  # Chặn video
    })
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

    # Start the service
    #user_profile = "C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"
    #chrome_options.add_argument("user-data-dir=" + user_profile)
    service = Service(webdriver_path)

    # Start the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def set_up_driver(url, service):
    '''Set up the driver and get url'''
    driver = configure_driver()

    # get url
    driver.get(url)
    return driver

def login_facebook(username, password, driver):
    '''Log in to Facebook'''

    try:
        # Wait 10s until the login form is loaded
        username_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "email")))
        username_field.send_keys(username)

        password_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "pass")))
        password_field.send_keys(password)

        # Submit log in form 
        password_field.send_keys(Keys.RETURN)

    except Exception as e:
        print("Logged in failed. \n")

    finally:
        print("Logged in successfully")
    

def log_out(driver):
    try:
        profile_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@aria-label="Trang cá nhân của bạn"]'))
            )
        profile_button.click()
        print("Đã nhấn nút Trang cá nhân của bạn thành công")
    except Exception as e:
        print(f"Không thể nhấn nút Trang cá nhân của bạn: {e}")

    # Đợi 3 giây để trang tải (nếu cần)
    time.sleep(3)

    # Tìm và nhấn nút Đăng xuất với class phức tạp và nội dung là "Đăng xuất"
    try:
        logout_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[text()="Đăng xuất"]'))
            )
        logout_button.click()
        print("Đã nhấn nút Đăng xuất thành công")
        return True
    except Exception as e:
        print(f"Không thể nhấn nút Đăng xuất: {e}")
        return False
    return False
