#! python3
"""
Script to log in to prenotami to check for appointments
every 30-60 minutes, except for 30 minutes +/- midnight Rome time 
(appointments should be done manually during this timeframe). Requires the 
schedule package (pip install schedule), selenium, and ChromeDriver.

Optional: set up an account with Twilio to send a text
whenever the script finds an available appointment.
"""

import schedule
import time
import datetime as dt
from pytz import timezone

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    __import__('twilio.rest')
except ImportError:
    print("Twilio package not found, option to send texts turned off.")
    twilio_text = False
else:
    from twilio.rest import Client
    twilio_text = True

# Runs job every 30-60 minutes
def prenota_job():

    # Gets current time
    current_time = dt.datetime.now()
    rome_time = dt.datetime.now().astimezone(timezone('Europe/Rome'))

    # Skips any time around midnight Rome time
    if rome_time.hour == 23:
        if rome_time.minute > 30:
            print(f'Not checking appointments at this time: {current_time.strftime("%H:%M:%S")}.')
            print(f'Checking again at {current_time + dt.timedelta(seconds=next_sched)}.')
            return None
    elif rome_time.hour == 0:
        if rome_time.minute < 30:
            print(f'Not checking appointments at this time: {current_time.strftime("%H:%M:%S")}.')
            print(f'Checking again at {current_time + dt.timedelta(seconds=next_sched)}.')
            return None

    # Sets up Chromedriver options
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--headless=new")

    # Launches headless browser
    driver = webdriver.Chrome(options=options)

    # Delcares explicit max wait time (seconds) for a page to load
    wait_time = 30

    # Declares time to wait before attempting to reload a page
    reload_time = 5

    # Navigates to the login page and enters credentials
    login_page = True
    while login_page == True:
        try:
            # Goes to webpage
            driver.get('https://prenotami.esteri.it/')

            # Enters email by clicking on field and typing
            clickable = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, usr_xpath)))
            webdriver.ActionChains(driver)\
                .move_to_element(clickable)\
                .pause(2)\
                .click_and_hold()\
                .pause(2)\
                .send_keys(usrnme)\
                .perform()
            
            # Enters password, same way
            clickable2 = driver.find_element(By.XPATH, pass_xpath)
            webdriver.ActionChains(driver)\
                .move_to_element(clickable2)\
                .pause(2)\
                .click_and_hold()\
                .pause(2)\
                .send_keys(passwd)\
                .perform()
            
            # Clicks login
            driver.find_element('xpath', "/html/body/main/div/section[1]/form/button").click()
    
            login_page = False
            print('Login page success!')
    
        except TimeoutException:
            print('Login page not loading, trying again.')
            time.sleep(reload_time)

    # Checks if able to navigate directly to citizenship appointment booking screen
    booking_screen_url = 'https://prenotami.esteri.it/Services/Booking/232'
    booking_page = True
    while booking_page == True:
        try:
            driver.get(booking_screen_url)
            header_xpath = '/html/body'
            # Waits for the page to load, up to declared wait_time
            check_loaded = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, 
                                                                                                  header_xpath)))
            booking_page = False
        except TimeoutException:
            print('Booking page not loading, trying again.')
            time.sleep(reload_time)
            
    # Gets current url
    url = driver.current_url

    # If able to navigate directly to booking screen:
    if url == booking_screen_url:
        print('Appointments available!')
        
        # Sends text if option enabled
        if twilio_text == True:
            message = client.messages \
            .create(
                 body=f'Prenotami appointments available! {url}',
                 from_=twilio_from,
                 to=twilio_to
             )

        # Closes browser window
        driver.close()

        # Cancels remaining jobs if appointments are found
        schedule.CancelJob
        
    else:
        # If no appointments are found, print to command line and run again
        current_time = dt.datetime.now()
        print(f'No available appointments at {current_time.strftime("%H:%M:%S")}.')
        
        next_runtime = schedule.next_run().strftime("%H:%M:%S")
        print(f'Checking again at {next_runtime}.')
    
        # Closes browser window
        driver.close()
        
# Update this with your prenotami login info!
usrnme = "XXXXXX"
passwd = "XXXXXX"

if usrnme == "XXXXXX":
    raise ValueError(f"Change username in script from default: {usrnme}.")
if passwd == "XXXXXX":
    raise ValueError(f"Change password in script from default: {passwd}.")

# Change this to outgoing Twilio number (optional)
twilio_from = '+1XXXXXXXXXX'

# Change this to incoming cell number (optional)
twilio_to = '+1XXXXXXXXXX'

# Your Account SID from twilio.com/console (optional)
account_sid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Your Auth Token from twilio.com/console (optional)
auth_token  = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# Makes sure Twilio variables are set if option is toggled on
if twilio_text == True:
    if twilio_from == '+1XXXXXXXXXX':
        raise ValueError(f"Change outgoing Twilio number from default: {twilio_from}.")
    if twilio_to == '+1XXXXXXXXXX':
        raise ValueError(f"Change incoming cell number from default: {twilio_to}.")
    if account_sid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
        raise ValueError(f"Change Twilio account SID from default: {account_sid}.")
    if auth_token = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
        raise ValueError(f"Change Twilio auth token from default: {auth_token}.")

# Run job every 30-60 minutes
schedule.every(30).to(60).minutes.do(prenota_job)

while True:
    # Schedules jobs
    schedule.run_pending()
    next_sched = schedule.idle_seconds()
    time.sleep(next_sched)





    
    


