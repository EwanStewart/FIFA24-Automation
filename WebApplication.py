import os
import time
import requests
import datetime
import subprocess
import random

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

class WebApplication:

    profile_to_use = "Default"
    server_url = "http://192.168.1.210/?new_message="
    debug_url = "http://192.168.1.210/?new_debug_message="

    dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir, "shutdown-pc.bat")  
    out_filename = os.path.join(dir, "wasReprice.out")
    isReprice = 0
    players = {}

    def __init__(self, isDebug, isShutdown):

        self.debug = isDebug
        self.shutdown = isShutdown
        self.getLastRun()
        self.createBrowserInstance()
        self.loginToWebApp()

    def createBrowserInstance(self):

        '''
        Create an instance of Chrome Driver using
        the specified user directory.
        '''

        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63'

        options = Options()
        options.add_argument("user-agent=" + user_agent)
        options.add_argument("--user-data-dir=C:/Users/ewans/AppData/Local/Google/Chrome/User Data/")
        options.add_argument("--profile-directory=" + self.profile_to_use)     

        self.chromeBrowser = webdriver.Chrome(options=options)
        self.chromeBrowser.get('https://www.ea.com/fifa/ultimate-team/web-app/')

    
    def logMessageToServer(self, msg, force_msg):

        '''
        Sends a message to local server to track script
        progress.
        '''
        if self.debug:
            url = self.debug_url

        if force_msg:
            url = self.server_url
        
        if url:
            data = {"timestamp": datetime.datetime.now().isoformat()}
            requests.get(url + msg, params=data)

    def loginToWebApp(self):
        self.logMessageToServer("Relist Script has been started.", False)

        # Initial login button after loading animation.
        try:
            WebDriverWait(self.chromeBrowser, 10).until(
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
            WebDriverWait(self.chromeBrowser, 15).until(
                ec.element_to_be_clickable((
                    By.XPATH, '//*[@id="logInBtn"]'))
                    ).click()
        except:
            '''
            If this further login button does not appear,
            we can continue as normal.
            '''
            pass

        try:
            WebDriverWait(self.chromeBrowser, 15).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/div[4]/div/div[2]/button'))
                    ).click()
        except:
            '''
            If this further login button does not appear,
            we can continue as normal.
            '''
            pass

    def wait_and_click(self, xpath):
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, xpath))).click()


    def scanClub(self):
        self.wait_and_click("/html/body/main/section/nav/button[5]")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div[1]")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div/div[1]/span[3]/button")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div/div[1]/div[1]/div[2]")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div/div[1]/div[1]/div[2]/div/ul/li[3]")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div/div[2]/button[2]")

        time.sleep(2)

        while True:
            main_views = self.chromeBrowser.find_elements(By.CLASS_NAME, "ut-item-view--main")

            for main_view in main_views:
                player_overview = main_view.find_element(By.CLASS_NAME, "playerOverview")
                grandparent = main_view.find_element(By.XPATH, "..//parent::*//parent::*")
                name = grandparent.find_element(By.CLASS_NAME, "name").text
                rating_element = player_overview.find_element(By.CLASS_NAME, "rating")
                rating_text = rating_element.text


                if not rating_text:
                    continue
     
                if (int(rating_text) < 83):
                    return

                if name in self.players:
                    continue

                self.players[name] = int(rating_text)

            self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div/div[3]/div/button[2]")



    def getToTransferMarket(self):
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/nav/button[3]'))).click()
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[2]/div[2]'))).click() 

    def commonGoldBids(self, pages):
        self.getToTransferMarket()

        '''
        Player Button
        '''
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[1]/div/button[1]'))).click() 

        '''
        Reset
        '''
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[2]/button[1]'))).click() 

        '''
        Quality -> Gold
        '''
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2] '))).click() 
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div/ul/li[4]'))).click() 

        '''
        Rarity -> Common
        '''
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[3]'))).click() 
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div/ul/li[2]'))).click() 
    
        '''
        Set Max Bid
        '''
        for i in range(0,4):
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[3]/div[2]/button[2]'))).click() 

        '''
        Search
        '''
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[2]/button[2]'))).click() 

        for i in range(0,4):
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[1]/div/div/button[2]'))).click() 
            time.sleep(0.5)

        time.sleep(2)

        for i in range(0, pages):
            player_auctions = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data")

            for i in range(0,len(player_auctions)):
                player_auctions[i].click()
                element = self.chromeBrowser.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[1]/div/div[2]/span[2]").text

                if int(element) == 300:
                    WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/button[1]'))).click() 
                time.sleep(1)

            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[1]/div/div/button[2]'))).click() 
            time.sleep(2)
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/nav/button[3]'))).click()


    def getToSBC(self):
        WebDriverWait(self.chromeBrowser, 15).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/nav/button[6]'))
                ).click()
        
        time.sleep(1)

    def EightyOnePlusPP(self):
        
        h1_element = self.chromeBrowser.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='80+ Player Pick']")
        div = h1_element.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='80+ Player Pick']/ancestor::*[3]")
        div.click()

        try:
            WebDriverWait(self.chromeBrowser, 2).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/section/div/div[2]/button[3]'))
                    ).click()
            WebDriverWait(self.chromeBrowser, 2).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))
                    ).click()
        except:
            pass
        
        a = ""
        positionsToFill = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-squad-slot-view:not(.ut-squad-slot-view.locked)")
        for i in range(0, 6):
            try:
                positionsToFill[i].click()
            except:
                WebDriverWait(self.chromeBrowser, 5).until(
                    ec.element_to_be_clickable((
                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/div[1]/div[1]'))
                        ).click()
                
                positionsToFill[i].click()

            '''
            Add player.
            '''
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div[2]/div[2]/button[3]'))
                    ).click()
                        
            '''
            Reset.
            '''

            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[3]/button[1]'))
                    ).click()
                        
            '''
            Sort by button.
            '''
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[1]/div[2]'))
                    ).click()
                        
            '''
            Low-to-High.
            '''
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[1]/div[2]/div/ul/li[4]'))
                    ).click()
                        
            '''
            Quality button.
            '''

        
            if (i == 5):
                rarity = 3
            else:
                rarity = 2

            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[3]/div/div'))
                    ).click()
            
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[3]/div/ul/li[4]'))
                    ).click()
                        
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[5]/div/div/button'))
                    ).click()
                        
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[4]/div/div'))
                    ).click()
                        
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[4]/div/ul/li['+str(rarity)+']'))
                    ).click()
                        
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[1]/div[1]/div[2]/div/div[2]'))
                    ).click()
                        
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[3]/button[2]'))
                    ).click()
                        
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div[3]/ul/li[1]/button'))
                    ).click()
            
            if (i == 5):
                rating = WebDriverWait(self.chromeBrowser, 5).until(
                    ec.element_to_be_clickable((
                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[1]/ul/li/div/div[1]/div[1]/div[4]/div[2]/div[1]'))
                        ).text
                print(rating)
                
                if (int(rating) > 82):
                    return
            
            time.sleep(2)
            positionsToFill = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-squad-slot-view:not(.ut-squad-slot-view.locked)")
        WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/div[2]/button[2]'))
                    ).click()
        
        for i in range(0,2):
            try:
                WebDriverWait(self.chromeBrowser, 5).until(
                        ec.element_to_be_clickable((
                            By.XPATH, '/html/body/div[4]/div/footer/button'))
                            ).click()
            except:
                pass

    def EightyThreeTimes10(self):
        self.getToSBC()
        h1_element = self.chromeBrowser.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='83+ x10 Upgrade']")
        div = h1_element.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='83+ x10 Upgrade']/ancestor::*[3]")
        div.click()

        matching_keys = [key for key, value in self.players.items() if value == 83]

        try:
            WebDriverWait(self.chromeBrowser, 2).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/section/div/div[2]/button[3]'))
                    ).click()
            WebDriverWait(self.chromeBrowser, 2).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))
                    ).click()
        except:
            pass
        
        a = ""
        positionsToFill = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-squad-slot-view:not(.ut-squad-slot-view.locked)")
        for i in range(0, 10):
            try:
                positionsToFill[i].click()
            except:
                WebDriverWait(self.chromeBrowser, 5).until(
                    ec.element_to_be_clickable((
                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/div[1]/div[1]'))
                        ).click()
                
                positionsToFill[i].click()

            '''
            Add player.
            '''
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div[2]/div[2]/button[3]'))
                    ).click()
                      
            bidPrice = WebDriverWait(self.chromeBrowser, 2).until(ec.element_to_be_clickable((
                By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[1]/div/div[1]/input"))
            )

            bidPrice.click()

            bidPrice.send_keys(Keys.CONTROL, 'a')
            bidPrice.send_keys(Keys.BACKSPACE)
            bidPrice.send_keys(matching_keys[i])
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[5]/div/div/button'))
                    ).click()
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[1]/div/div[2]/ul/button'))
                    ).click()

            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[3]/button[2]'))
                    ).click()        

            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div[3]/ul/li[1]/button'))
                    ).click() 

            time.sleep(2)
            positionsToFill = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-squad-slot-view:not(.ut-squad-slot-view.locked)")
        

    
    def getToTransferList(self):
        '''
        Click transfers on the left hand pane of the web application.
        Click transfer list within this window.
        '''
        WebDriverWait(self.chromeBrowser, 5).until(
            ec.presence_of_element_located((
                By.XPATH, '/html/body/main/section/nav/button[3]'))
                ).click()
        
        WebDriverWait(self.chromeBrowser, 5).until(
            ec.presence_of_element_located((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[3]'))
                ).click()
        
        self.logMessageToServer("Entered the transfer list.", False)

    def sendWonItemsToTransferList(self):
        '''
        Tranfers button on left hand pane of the application.
        '''
        WebDriverWait(self.chromeBrowser, 10).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/nav/button[3]'))
                ).click()  

        self.logMessageToServer("Login into the web application was successful.", False)
    
        '''
        Transfer targets within the transfers window.
        '''
        WebDriverWait(self.chromeBrowser, 10).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[4]'))
                ).click()   

        '''
        Clear players which were not won during the bidding process.
        If this button is not clickable, then we can continue as normal as
        there are no expired transfers.
        '''
        try:
            WebDriverWait(self.chromeBrowser, 10).until(
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
        won_items = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data.won")

        for item in won_items:
            item.click() # Focus the item.

            try:
                isPlayer = item.find_element(By.CSS_SELECTOR, "div.small.player.item")
            except:
                isPlayer = False
                
            if (isPlayer):
                try:
                    WebDriverWait(self.chromeBrowser, 10).until(
                        ec.element_to_be_clickable((
                            By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[3]/button[6]'))
                            ).click()
                except:
                    '''
                    Assume the transfer list is full.
                    '''
                    continue
            else:
                try:
                    WebDriverWait(self.chromeBrowser, 10).until(
                        ec.element_to_be_clickable((
                            By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[3]/button[8]'))
                            ).click()
                except:
                    '''
                    Assume the transfer list is full.
                    '''
                    continue
            
            time.sleep(1)

        coinTotal =     WebDriverWait(self.chromeBrowser, 10).until(
                            ec.presence_of_element_located((
                                By.XPATH, '/html/body/main/section/section/div[1]/div[1]/div[1]'))
                                ).text
        
        self.logMessageToServer(str(coinTotal), True)
        self.logMessageToServer("All items have been added to the transfer list.", False)

    def relistItemsOnly(self):
        self.logMessageToServer("Items relist only has begun.", False)
        time.sleep(5) # Allow web application to load assets.

        '''
        Attempt to clear any sold items in the transfer list,
        wait to allow application to update.
        If none sold continue as normal.
        '''
        try:
            WebDriverWait(self.chromeBrowser, 5).until(
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
        WebDriverWait(self.chromeBrowser, 5).until(
            ec.presence_of_element_located((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/section[2]/header/button'))
                ).click()
            
        time.sleep(1)

        WebDriverWait(self.chromeBrowser, 5).until(
            ec.presence_of_element_located((
                By.XPATH, '/html/body/div[4]/section/div/div/button[2]'))
                ).click()
        
        time.sleep(10)

        self.logMessageToServer("All items have been relisted only.", False)

    def relistAndUpdatePrice(self):
        self.logMessageToServer("Items relist and reprice has begun.", False)

        time.sleep(5) # Allow web application to load assets.

        iterations = 0
        tolerated_failed_attempts = 0

        '''
        Attempt to clear any sold items in the transfer list,
        wait to allow application to update.
        If none sold continue as normal.
        '''
        try:
            WebDriverWait(self.chromeBrowser, 5).until(
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
                    WebDriverWait(self.chromeBrowser, 5).until(
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
                    WebDriverWait(self.chromeBrowser, 5).until(
                    ec.element_to_be_clickable((
                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[3]/button[9]'))
                        ).click() 
                
                    time.sleep(4)
                except:
                    continue_relist = False
                    self.logMessageToServer("Nothing to relist!", False)
                    '''
                    Down to the last item break from loop.
                    '''
                    break

                if continue_relist:
                    '''
                    Collate all item element shown from compare price.
                    Find lowest price out of the elements
                    '''

                    compare_prices_list = WebDriverWait(self.chromeBrowser, 5).until(
                        ec.visibility_of_element_located((By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div[2]/section/div[2]"))
                    )

                    buy_now_list = compare_prices_list.find_elements(By.XPATH, ".//span[text()='Buy Now:']")

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
                    WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((
                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[1]/button'))
                        ).click() 
                    
                    time.sleep(3)

                    '''
                    Relist the item, with the calculated lowest price.
                    '''
                    WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((
                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div[2]/div[2]/div[1]'))
                        ).click() 

                    bidPrice = WebDriverWait(self.chromeBrowser, 2).until(ec.element_to_be_clickable((
                        By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/input"))
                    )

                    bidPrice.click()
                    bidPrice.send_keys(Keys.CONTROL, 'a')
                    bidPrice.send_keys(Keys.BACKSPACE)
                    bidPrice.send_keys(list_price - 100)

                    buyNowPrice = WebDriverWait(self.chromeBrowser, 2).until(ec.element_to_be_clickable((
                        By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/div[3]/div[2]/input"))
                    ) 

                    buyNowPrice.click()
                    buyNowPrice.send_keys(Keys.CONTROL, 'a')
                    buyNowPrice.send_keys(Keys.BACKSPACE)
                    buyNowPrice.send_keys(list_price)
                            
                    WebDriverWait(self.chromeBrowser, 2).until(ec.element_to_be_clickable((
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
                    self.logMessageToServer("Too many errors breaking from relist loop!", False)
                    break
                else:
                    self.logMessageToServer("An error in the relist loop was handled!", False)
                    tolerated_failed_attempts += 1
                    continue
    
    def writeToOutFile(self, value):
        with open(self.out_filename, "w") as file:
            file.write(str(value))

    def readOutFile(self):
        with open(self.out_filename, "r") as file:
            return(file.readlines()[-1].strip())
        
    def XOR(self, x):
        return (int(x) ^ 1) # XOR to flip 0 or 1.

    def getLastRun(self):
        if os.path.exists(self.out_filename):
            self.isReprice = self.XOR(self.readOutFile())
        
        self.writeToOutFile(self.isReprice)
    
    def exitApplication(self):
        self.chromeBrowser.quit()

        if self.shutdown:
            '''
            After execution turn off the device.
            '''
            time.sleep(10)

            subprocess.Popen(self.file_path, shell=True, stdout = subprocess.PIPE).communicate()

    def relistOrReprice(self):
        if (self.isReprice):
            self.relistAndUpdatePrice()
        else:
            self.relistItemsOnly()
            '''
            A call to relistAndUpdatePrice after relistItemsOnly will ensure any new items
            that have been added to the transfer list are listed.
            '''
            self.relistAndUpdatePrice()

    def getNumberOfTransferListItems(self):
        return (100 - int(WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((
            By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[3]/div[2]/div/div[1]/span[1]'))
            ).text)
        )
    
    def contains_time_words(self, text):
        time_words = ["day", "days", "hour", "hours"]
        for word in time_words:
            if word.lower() in text.lower():
                return False
        return True

    def buyClubItems(self, isBadges):
        '''
        Navigate and apply filters:
            1. Transfers
            2. Search the Transfer Market
            3. Club Items
            4. Quality
            5. Silver
        '''
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/nav/button[3]'))).click()
        
        if (self.getNumberOfTransferListItems() <= 10):
            return
        
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[2]/div[2]'))).click() 
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[1]/div/button[3]'))).click() 
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div/div'))).click()
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div/ul/li[3]'))).click() 
        if isBadges:
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[5]/div/div'))).click()
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '    /html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[5]/div/ul/li[3]'))).click()

        '''
        Clear the previous maxBid and minBuyNow.
        '''
        maxBid = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[3]/div[2]/input')
        maxBid.click()
        maxBid.send_keys(Keys.CONTROL, 'a')
        maxBid.send_keys(Keys.BACKSPACE)

        minBuyNow = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[5]/div[2]/input')
        minBuyNow.click()
        minBuyNow.send_keys(Keys.CONTROL, 'a')
        minBuyNow.send_keys(Keys.BACKSPACE)

        '''
        Setup the min buy now price and max bid price.
        minBuyNow = 1000
        MaxBid = 350
        '''
        for i in range(0,4):
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[3]/div[2]/button[2]'))).click() #max bid

        for i in range(0,18):
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[5]/div[2]/button[2]'))).click() #min buy now
        
        '''
        Search and allow assets to load.
        '''
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[2]/button[2]'))).click()
        time.sleep(2)

        '''
        Gather all auctions on page and places a bid if the item is worth more than 1000 coins.
        '''
        listed = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data")

        for i in range(0,len(listed)-1):
            listed[i].click()
            time_text = listed[i].find_element(By.CSS_SELECTOR, "span.time").text
            if not (self.contains_time_words(time_text)):
                print("too long")
                return

            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[3]/button[2]'))).click() #compare
            try:
                time.sleep(2)
                list_element = WebDriverWait(self.chromeBrowser, 10).until(
                    ec.visibility_of_element_located((By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div[2]/section/div[2]"))
                )

                buy_now_spans = list_element.find_elements(By.XPATH, ".//span[text()='Buy Now:']")
                buy_now_prices = []

                for span in buy_now_spans:
                    price_element = span.find_element(By.XPATH, "./following-sibling::span")  # Assuming price is in a following span
                    price_text = (price_element.text)
                    buy_now_prices.append(price_text)

                if (buy_now_prices):
                    for i in range(len(buy_now_prices)):
                        buy_now_prices[i] = buy_now_prices[i].replace(",", "")  # Modify each item
                    buy_now_prices = list(map(int, buy_now_prices))
                    lowest_price = min(buy_now_prices)

                WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[1]/button'))).click() #back
                time.sleep(2)
                if lowest_price > 1000:
                    price_element = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/div/input')
                    price_element.click()
                    price_element.send_keys(Keys.CONTROL, 'a')
                    price_element.send_keys(Keys.BACKSPACE)
                    price_element.send_keys(str(lowest_price * 0.1))
                    WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/button[1]'))).click() #bid
                    try:
                        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))).click() #cancel re-bid
                    except:
                        pass
            except:
                pass

            time.sleep(2) # Apply delay between bids.



            
