# Ewan Stewart, 2024
# FC 24 automation script to relist and adjust prices of club items.

import time
import requests
import datetime
import random
import subprocess

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

PROFILE_TO_USE = "Default"
SERVER_URL = "http://192.168.1.210/?heartbeat="
FILE_PATH = "C:/Users/ewans/Desktop/shutdown.bat"
DEBUG = False

def createBrowserInstance():

    '''
    Create an instance of Chrome Driver using
    the specified user directory.
    '''

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63'

    options = Options()
    options.add_argument("user-agent=" + user_agent)
    options.add_argument("--user-data-dir=C:/Users/ewans/AppData/Local/Google/Chrome/User Data/")
    options.add_argument("--profile-directory=" + PROFILE_TO_USE)     

    return webdriver.Chrome(options=options)

def logMessageToServer(msg, force_msg):

    '''
    Sends a message to local server to track script
    progress.
    '''
    if DEBUG or force_msg:
        data = {"timestamp": datetime.datetime.now().isoformat()}
        requests.get(SERVER_URL + msg, params=data)

def loginToWebApp(chromeBrowser):
    # Initial login button after loading animation.
    try:
        WebDriverWait(chromeBrowser, 10).until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR, '#Login > div > div > button.btn-standard.call-to-action'))
                ).click()
    except:
        '''
        If this login button does not appear,
        we can continue as normal.
        '''
        pass

    '''
    A further login button appears occasionally.
    Login details are saved as part of the Chrome profile,
    however, it has been noticed that these details can be wiped.
    In this case manual intervention is required.
    '''
    try:
        WebDriverWait(chromeBrowser, 15).until(
            ec.element_to_be_clickable((
                By.XPATH, '//*[@id="logInBtn"]'))
                ).click()
    except:
        '''
        If this further login button does not appear,
        we can continue as normal.
        '''
        pass

def getToTransferList(browser):
    '''
    Click transfers on the left hand pane of the web application.
    Click transfer list within this window.
    '''
    WebDriverWait(browser, 5).until(
        ec.presence_of_element_located((
            By.XPATH, '/html/body/main/section/nav/button[3]'))
            ).click()
    
    WebDriverWait(browser, 5).until(
        ec.presence_of_element_located((
            By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[3]'))
            ).click()
    
    logMessageToServer("Entered the transfer list.", False)

def relistAndUpdatePrice(browser):
    logMessageToServer("Items relist has begun.", False)

    time.sleep(5) # Allow web application to load assets.

    iterations = 0
    tolerated_failed_attempts = 0

    '''
    Attempt to clear any sold items in the transfer list,
    wait to allow application to update.
    If none sold continue as normal.
    '''
    try:
        WebDriverWait(browser, 5).until(
            ec.presence_of_element_located((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/section[1]/header/button'))
                ).click()
        time.sleep(2)
    except:
        pass
    
    continue_relist = True
    '''
    While valid items exist to be listed continue.
    '''
    while (1):
        try:
            iterations += 1
            if iterations >= 100:
                break

            list_price = None # Reset lowest price every iteration to ensure prices are always updated.
            buy_now_prices = []

            '''
            Attempt to clear any sold items in the transfer list,
            wait to allow application to update.
            If none sold continue as normal.
            '''
            try:
                WebDriverWait(browser, 5).until(
                    ec.presence_of_element_located((
                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/section[1]/header/button'))
                        ).click()
                time.sleep(2)
            except:
                pass

            '''
            Press compare on the selected item and wait for application to update.
            '''
            try:
                WebDriverWait(browser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[3]/button[9]'))
                    ).click() 
            
                time.sleep(4)
            except:
                continue_relist = False
                logMessageToServer("Nothing to relist!", False)
                '''
                Down to the last item break from loop.
                '''
                break

            if continue_relist:
                '''
                Collate all item element shown from compare price.
                Find lowest price out of the elements
                '''

                comapre_prices_list = WebDriverWait(browser, 5).until(
                    ec.visibility_of_element_located((By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div[2]/section/div[2]"))
                )

                buy_now_list = comapre_prices_list.find_elements(By.XPATH, ".//span[text()='Buy Now:']")

                for span in buy_now_list:
                    price_element = span.find_element(By.XPATH, "./following-sibling::span") 
                    buy_now_prices.append(price_element.text)

                '''
                If there is a valid list of prices,
                a list price can be calculated by:
                lowest price found less ten percent.
                '''

                if (buy_now_prices):

                    for i in range(len(buy_now_prices)):
                        buy_now_prices[i] = buy_now_prices[i].replace(",", "")  # Remove commas to allow for convert to integer.

                    '''
                    Convert to integer and calculate min price.
                    '''
                    buy_now_prices = list(map(int, buy_now_prices))
                    list_price = min(buy_now_prices)

                    '''
                    If no price data list for max.
                    '''
                    if list_price == None:
                        list_price = 5000

                    list_price -= list_price * 0.1

                    '''
                    Ensure items aren't listed for min price.
                    '''
                    if list_price <= 200:
                        list_price = 300
                        
                '''
                If something has went wrong ensure the price is max.
                '''
                if list_price == None:
                    list_price = 5000
                
                '''
                Take compare price list out of focus.
                Allow application to process.
                '''
                WebDriverWait(browser, 5).until(ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[1]/button'))
                    ).click() 
                
                time.sleep(3)

                '''
                Relist the item, with the calculated lowest price.
                '''
                WebDriverWait(browser, 5).until(ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div[2]/div[2]/div[1]'))
                    ).click() 

                bidPrice = WebDriverWait(browser, 2).until(ec.element_to_be_clickable((
                    By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/input"))
                )

                bidPrice.click()
                bidPrice.send_keys(Keys.CONTROL, 'a')
                bidPrice.send_keys(Keys.BACKSPACE)
                bidPrice.send_keys(list_price - 100)

                buyNowPrice = WebDriverWait(browser, 2).until(ec.element_to_be_clickable((
                    By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/div[3]/div[2]/input"))
                ) 

                buyNowPrice.click()
                buyNowPrice.send_keys(Keys.CONTROL, 'a')
                buyNowPrice.send_keys(Keys.BACKSPACE)
                buyNowPrice.send_keys(list_price)
                        
                WebDriverWait(browser, 2).until(ec.element_to_be_clickable((
                    By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/button"))
                ).click() # Confirm Price.

                time.sleep(2)
        except:
            '''
            Due to the nature of the web application,
            failures may occur when simulating button presses.
            Allow for 10 button interactions to fail before breaking the loop.
            '''
            if tolerated_failed_attempts >= 10:
                logMessageToServer("Too many errors breaking from relist loop!", False)
                break
            else:
                logMessageToServer("An error in the relist loop was handled!", False)
                tolerated_failed_attempts += 1
                continue

def relistItemsOnly(browser):
    time.sleep(5) # Allow web application to load assets.

    '''
    Attempt to clear any sold items in the transfer list,
    wait to allow application to update.
    If none sold continue as normal.
    '''
    try:
        WebDriverWait(browser, 5).until(
            ec.presence_of_element_located((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/section[1]/header/button'))
                ).click()
        time.sleep(2)
    except:
        pass

    '''
    Press relist all and press confirm.
    Wait after relist to ensure items are listed.
    '''
    WebDriverWait(browser, 5).until(
        ec.presence_of_element_located((
            By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/section[2]/header/button'))
            ).click()
        
    time.sleep(1)

    WebDriverWait(browser, 5).until(
        ec.presence_of_element_located((
            By.XPATH, '/html/body/div[4]/section/div/div/button[2]'))
            ).click()
    
    time.sleep(5)

    logMessageToServer("All items have been relisted only.", False)

def sendWonItemsToTransferList(browser):
    '''
    Tranfers button on left hand pane of the application.
    '''
    WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable((
            By.XPATH, '/html/body/main/section/nav/button[3]'))
            ).click()  

    logMessageToServer("Login into the web application was successful.", False)
   
    '''
    Transfer targets within the transfers window.
    '''
    WebDriverWait(browser, 10).until(
        ec.element_to_be_clickable((
            By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[4]'))
            ).click()   

    '''
    Clear players which were not won during the bidding process.
    If this button is not clickable, then we can continue as normal as
    there are no expired transfers.
    '''
    try:
        WebDriverWait(browser, 10).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/section[4]/header/button[1]'))
                ).click()
    except:
        pass

    '''
    Wait several seconds to allow for the web application to update,
    if there are expired items to clear.
    '''
    time.sleep(2)

    '''
    Locate all items which were won during the bidding process,
    enumerate through these items and send them to the transfer list.
    A wait between items is required to allow the application to update.
    '''
    won_items = browser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data.won")

    for item in won_items:
        item.click() # Focus the item.

        time.sleep(1)

        WebDriverWait(browser, 10).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[3]/button[8]'))
                ).click()
        
        time.sleep(1)

    coinTotal =     WebDriverWait(browser, 10).until(
                        ec.presence_of_element_located((
                            By.XPATH, '/html/body/main/section/section/div[1]/div[1]/div[1]'))
                            ).text
    
    logMessageToServer(str(coinTotal), True)
    logMessageToServer("All items have been added to the transfer list.", False)

def main():
    logMessageToServer("Relist Script has been started.", False)
    chromeBrowser = createBrowserInstance()
    chromeBrowser.get('https://www.ea.com/fifa/ultimate-team/web-app/')
    try:
        loginToWebApp(chromeBrowser)
        sendWonItemsToTransferList(chromeBrowser)
        getToTransferList(chromeBrowser)

        generatedNumber = random.randint(1, 10)
        if (generatedNumber) <= 6:
            relistAndUpdatePrice(chromeBrowser)
        else:
            relistItemsOnly(chromeBrowser)
            '''
            A call to relistAndUpdatePrice after relistItemsOnly will ensure any new items
            that have been added to the transfer list are listed.
            '''
            relistAndUpdatePrice(chromeBrowser)
    except:
        pass
    finally:
        chromeBrowser.quit()

main()

'''
After execution turn off the device.
'''
time.sleep(10)

p = subprocess.Popen(FILE_PATH, shell=True, stdout = subprocess.PIPE)
stdout, stderr = p.communicate()