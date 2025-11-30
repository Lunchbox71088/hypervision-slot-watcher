"""
Hypervision Slot Watcher (safe – no checkout submission)
Checks the checkout page for slot availability and sends an SMS alert.
"""

import time, smtplib, chromedriver_autoinstaller
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -----------------------------------------------------------
URL = "https://hypervision.gg/checkout/?prod=1"
CHECK_INTERVAL = 90  # seconds
# -----------------------------------------------------------

# ---- Configure your own email credentials ----
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"          # Gmail app password
SMS_GATEWAY   = "3022170146@vtext.com"        # or @mypixmessages.com
# ----------------------------------------------

chromedriver_autoinstaller.install()

opts = Options()
opts.add_argument("--headless=new")   # comment out if you want to see Chrome
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-gpu")

def send_text_alert():
    """Send an SMS text alert via Gmail."""
    msg = EmailMessage()
    msg["From"], msg["To"] = EMAIL_ADDRESS, SMS_GATEWAY
    msg["Subject"] = "🚨 HV COD Slot Available!"
    msg.set_content(f"A slot appears to be open:\n{URL}")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        s.send_message(msg)
    print("✅ Text alert sent")

def slot_available(driver) -> bool:
    """Return True if the page looks like slots are open."""
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
        )
        disabled = btn.get_attribute("disabled")
        text = btn.text.lower()
        page_text = driver.page_source.lower()

        if "no slots remaining" in page_text:
            return False
        if disabled or "unavailable" in text:
            return False
        return True
    except Exception as e:
        print("Error checking page:", e)
        return False

print("🚀 Starting Hypervision watcher ...")
driver = webdriver.Chrome(options=opts)

try:
    while True:
        driver.get(URL)
        if slot_available(driver):
            print("🎯 Possible slot detected — sending alert and stopping.")
            send_text_alert()
            break
        print(f"❌ Still full. Checking again in {CHECK_INTERVAL} seconds ...")
        time.sleep(CHECK_INTERVAL)
finally:
    driver.quit()
