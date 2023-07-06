#! python3
"""
Script to log in to prenotami to check for appointments
every hour on the 18th minute. Requires the schedule package
(pip install schedule), selenium, and ChromeDriver.

Optional: set up an account with Twilio to send a text
whenever the script finds an available appointment (never tested).
"""

import schedule
import time
import datetime as dt

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    __import__('twilio.rest')
except ImportError:
    print("Twilio package not found, option to send texts turned off.")
    twilio_text = False
else:
    from twilio.rest import Client
    twilio_text = True

# Runs job every hour on the hour
def prenota_job():

    url = r"https://prenotami.esteri.it/"
    
    # Update this with your prenotami login info!
    usrnme = "XXXXXX"
    passwd = "XXXXXX"
    
    if usrnme == "XXXXXX" or passwd == "XXXXXX":
        raise ValueError(f"Change username and/or password in script from default: {usrnme, passwd}.")

    options = Options()
    options.add_argument("--window-size=1920,1200")
    options.headless = True

    driver = webdriver.Chrome(options=options)
    
    wait_time = 300
    reload_time = 10
    
    result=None
    while result is None:
        try:
            driver.get(url)
            result = 'Not none!'
        except Exception:
            print("Home page isn't loading, trying again.")
            time.sleep(reload_time)

    # Waits up to 5 minutes for login page to load, then clicks and enters email
    result=None
    while result is None:
        try:
            clickable = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.ID, "login-email")))
            webdriver.ActionChains(driver)\
                .move_to_element(clickable)\
                .pause(2)\
                .click_and_hold()\
                .pause(2)\
                .send_keys(usrnme)\
                .perform()

            # Enters password
            clickable2 = driver.find_element(By.ID, "login-password")
            webdriver.ActionChains(driver)\
                .move_to_element(clickable2)\
                .pause(2)\
                .click_and_hold()\
                .pause(2)\
                .send_keys(passwd)\
                .perform()

            # Clicks on submit to login                                
            driver.find_element_by_xpath("/html/body/main/div/section[1]/form/button").click()
            driver.implicitly_wait(2)
            print('Login page success!')
            result='Not none!'
        except Exception:
            print('Login page not loading, trying again.')
            time.sleep(reload_time)
            
    result=None
    while result is None:
        try:
            # Clicks on "Book"
            WebDriverWait(driver, wait_time)\
            .until(EC.presence_of_element_located((By.XPATH, "/html/body/main/nav/ul[1]/li[3]/a")))\
            .click()
            driver.implicitly_wait(1)
            print('Booking page success!')
            result='Not none!'
        except Exception:
            print('Booking page not loading, trying again.')
            time.sleep(reload_time)
        
    result=None
    while result is None:
        try:
            # Clicks on "Book" again under Appointments
            WebDriverWait(driver, wait_time)\
            .until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div[3]/div/table/tbody/tr[3]/td[4]/a/button")))\
            .click()
            driver.implicitly_wait(1)

            # Figures out if "no available appointments" window pops up
            no_appts = 'Al momento non ci sono date disponibili per il servizio richiesto'
            while result is None:
                try:
                    appts = WebDriverWait(driver, wait_time).\
                    until(EC.text_to_be_present_in_element((By.XPATH, 
                                                            "/html/body/div[2]/div[2]/div/div/div/div/div/div/div/div[3]/div/div"), 
                                                           no_appts))
                    if appts:
                        current_time = dt.datetime.now()
                        print(f'No available appointments at {current_time.strftime("%H:%M:%S")}.')
                        next_time = current_time + dt.timedelta(seconds=next_sched)
                        print(f'Checking again at {next_time.strftime("%H:%M:%S")}.')
                        result='Not none!'
                    else:
                        print('Available appointments!')
                        if twilio_text == True:
                            message = client.messages.create(
                            to="+1XXXXXXXXXX", # Your cell phone number here
                            from_="+1XXXXXXXXXX", # Your twilio number here
                            body=f"Check Prenota for appointments! {url}")
                        result='Not none!'
                except WebDriverException:
                    print("Something went wrong with appointments page.")
                    result=None
                    time.sleep(reload_time)
                else:
                    result='Not none!'

        except Exception as e:
            print('Appointments page not loading, trying again.')
            result=None
            time.sleep(reload_time)
        else: 
            result='Not none!'
            driver.close()
            

if twilio_text == True:
    # Your Account SID from twilio.com/console
    account_sid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    # Your Auth Token from twilio.com/console
    auth_token  = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    client = Client(account_sid, auth_token)

# Run job every hour on the 18th minute of the hour
schedule.every().hour.at(":18").do(prenota_job)

while True:
    # run_pending needs to be called on every scheduler
    schedule.run_pending()
    next_sched = schedule.idle_seconds()
    time.sleep(next_sched)





    
    


