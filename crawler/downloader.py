import os, sys

top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not top_path in sys.path:
    sys.path.insert(1, top_path)

from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

import tweepy
import pprint
import wget
from time import sleep
import traceback

from urllib import request

import re

def construct_image_file_name_from_twitter_url(url):
    file_name = None
    matches = re.search(".*/media/([^?]+).*format=([^&]+)", url)
    if matches is not None and len(matches.groups()) == 2:
        file_name = "%s.%s" % (matches.group(1), matches.group(2))
        
    return file_name

# Separate this into a function in case in future we need to do more complicated
# processing like renaming the file, sanitizing filename, etc.
def download_image_into_folder(url, folder):
    
    file_name = construct_image_file_name_from_twitter_url(url)

    # Define the local filename to save data
    local_file = os.path.join(folder, file_name)

    # Download remote and save locally
    request.urlretrieve(url, local_file)

    return local_file 

def grab_using_selenium(search_keyword, config):

    folder = config["TEMPORARY_FOLDER"]
    image_count_limit = config["IMAGE_COUNT_LIMIT"]
    browser_mode = config["BROWSER_MODE"]
    chrome_driver_path = config["CHROMEDRIVER_PATH"]
    twitter_user_name = config["TW_USER_NAME"]
    twitter_email = config["TW_EMAIL"]
    twitter_pwd = config["TW_PASSWORD"]

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--headless')    
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    display = None

    try:
        if browser_mode == 'headless':
            # Start a null display to allow headless operation of the browser
            print(">> Starting a null display", flush=True)
            display = Display(visible=0, size=(1500, 1000))
            display.start()

        # Start the selenium driver.
        # In production env, the driver (and display) might need to be moved out from this function
        # so that we don't restart from scratch everytime we call this function for efficiency.
        print(">> Starting a selenium driver", flush=True)
        driver = webdriver.Chrome(chrome_driver_path, chrome_options=chrome_options)          
        driver.set_window_size(1500, 1000)

        # Go to twitter login page and login  
        print(">> Logging in into Twitter", flush=True)      
        driver.get('https://twitter.com/login')
        sleep(0.2)

        # Twitter login has some variations to it, handle it.
        # Try to get to the username text box
        try:
            username_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@name="username"]')))
        except:                        
            username_field = driver.find_element_by_xpath('//input')

        if username_field is not None:
            # Once we found the username box, fill out the user_name            
            username_field.send_keys(twitter_email)

        sleep(0.3)

        WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//span[text()="Next"]'))).click()

        sleep(0.3)

        # Handle another variation on the twitter page, where they say something like
        # "Unusually high count of attempt ..."

        unusual_prompt = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, '//span[text()="Phone or username"]')))

        if unusual_prompt is not None:            

            WebDriverWait(driver, 4).until(
                        EC.presence_of_element_located((By.XPATH, '//input'))).send_keys(twitter_user_name)

            WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//span[text()="Next"]'))).click()

        sleep(0.3)

        # Fill out the password
        WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@name="password"]'))).send_keys(twitter_pwd)

        sleep(0.3)

        WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//span[text()="Log in"]'))).click() 

        sleep(0.3)

        # If we get to this point, we've logged in! Whoohoo!
        # Now locate the Search text box.

        search_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@aria-label="Search query"]')))
                        
        # Once we found the Search box, type the search string
        # Since for this test, the focus is images, use the "filter:images" in the search.          
        if search_field is not None:
            search_string = "%s filter:images" % search_keyword
            print(f">> Searching for: {search_string}", flush=True)  
            search_field.send_keys(search_string)   
            search_field.send_keys(Keys.RETURN)            
            
        sleep(0.3)
        
        # Need to force scroll down a few pages to get enough entries to show up
        # Future Improvement: don't hardcode the 25 repetition, should be able
        # to keep track how many images we got so far and do a page down only
        # when we need to.
        body = driver.find_element_by_tag_name('body')
        print(">> Scrolling down the search results", flush=True)  
        for i in range(25):
            body.send_keys(Keys.PAGE_DOWN)
            sleep(0.1)

        sleep(1)
        
        result_container = driver.find_element_by_xpath('//section[@role="region"]')        

        # Go thru the search results and look for images we can pull.
        # Try to skip any icons, logos, avatars, etc.
        # Example of twitter image that we can pull looks like this:
        #    https://pbs.twimg.com/media/FDQ6z9nXMAMmwE5?format=jpg&name=900x900
        # So filter for the word "media".
        # Obviously there are better ways that we can use in production.
        print(">> Parsing for images that we can use", flush=True)
        if result_container is not None:
            img_candidates = result_container.find_elements_by_xpath('//img[contains(@src, "media")]')        

        print(f">> Found {len(img_candidates)} image candidates, we should just pick 5", flush=True)

        # Now, download the images up to the specified limit
        result = []
        counter = 0    
        for img_candidate in img_candidates:
            if counter >= image_count_limit:
                break
            src = img_candidate.get_attribute("src")
            downloaded_file_path = download_image_into_folder(src, folder)
            print(f">> Downloading {src} --> {downloaded_file_path}", flush=True)
            result.append({
                "src": src,
                "local_file": downloaded_file_path
            })
            counter += 1

            sleep(1)
            
    finally:
        traceback.print_exc()
        # Shutdown
        print(">> Shutting down selenium driver and null display if any", flush=True)
        if driver is not None:            
            driver.quit()            
            sleep(0.5)
        if display is not None:
            display.stop()

    return result

