import os
import time
import requests
import datetime
import subprocess
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

SILVER_QUALITY = 3
SILVER_LOW = 65
SILVER_HIGH = 74
GOLD_QUALITY = 4
GOLD_LOW = 75
GOLD_HIGH = 82

STADIUM_PAINT = 3
SEAT_PAINT = 4
PITCH_PAINT = 1

class SBC:
    def __init__(self, title, rarity, numberOfPlayers, low, high, numberOfRares, rarityMatters):
        self.title = title
        self.quality = rarity
        self.numberOfPlayers = numberOfPlayers
        self.low = low
        self.high = high
        self.numberOfRares = numberOfRares
        self.rarityMatters = rarityMatters

class WebApplication:

    profile_to_use = "Default"
    server_url = "http://192.168.1.210/?new_message="
    debug_url = "http://192.168.1.210/?new_debug_message="
    price_url = "http://192.168.1.210/?write=1"
    blacklist_url = "http://192.168.1.210/?blacklist"

    dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir, "shutdown-pc.bat")  
    out_filename = os.path.join(dir, "wasReprice.out")
    isReprice = 0
    players = {}
    profileRequired = True


    def __init__(self, isDebug, isShutdown, isWait):

        self.debug = isDebug
        self.shutdown = isShutdown
        self.safeEntry = isWait
        self.getBlacklisted()
        self.getLastRun()
        self.createBrowserInstance()
        self.loginToWebApp()

    def getBlacklisted(self):
        try:
            response = requests.get(self.blacklist_url)
        except:
            pass
        self.blacklist = [color.strip() for color in response.text.split('<br>') if color.strip()]
        
    def createBrowserInstance(self):

        '''
        Create an instance of Chrome Driver using
        the specified user directory.
        '''

        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63'

        options = Options()
        options.add_argument("user-agent=" + user_agent)
        if (self.profileRequired):
            options.add_argument("--user-data-dir=C:/Users/ewans/AppData/Local/Google/Chrome/User Data/")
            options.add_argument("--profile-directory=" + self.profile_to_use)  
        options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
 
        options.add_experimental_option("useAutomationExtension", False)    

        self.chromeBrowser = webdriver.Chrome(options=options)
        self.chromeBrowser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
    
    def logMessageToServer(self, msg, force_msg):

        '''
        Sends a message to local server to track script
        progress.
        '''

        url = None
        
        if self.debug:
            url = self.debug_url

        if force_msg:
            url = self.server_url
        
        if url:
            data = {"timestamp": datetime.datetime.now().isoformat()}
            try:
                requests.get(url + msg, params=data)
            except:
                pass

    def loginToWebApp(self):
        self.chromeBrowser.get('https://www.ea.com/fifa/ultimate-team/web-app/')
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

        if self.safeEntry:
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

    def fillSBC(self):
        url = "https://www.easysbc.io/"
        self.chromeBrowser.execute_script("window.open('" + url +"');")
        while (1):
            input('Press Enter to continue...')
            pass




    def scanClub(self, threshold):
        self.wait_and_click("/html/body/main/section/nav/button[5]")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div[1]")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div/div[1]/span[3]/button")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div/div[1]/div[1]/div[2]")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div/div[1]/div[1]/div[2]/div/ul/li[3]")
        self.wait_and_click("/html/body/main/section/section/div[2]/div/div/div/div[2]/button[2]")

        time.sleep(2)

        while True:
            time.sleep(0.5)
            main_views = self.chromeBrowser.find_elements(By.CLASS_NAME, "ut-item-view--main")

            for main_view in main_views:
                player_overview = main_view.find_element(By.CLASS_NAME, "playerOverview")
                grandparent = main_view.find_element(By.XPATH, "..//parent::*//parent::*")
                name = grandparent.find_element(By.CLASS_NAME, "name").text
                rating_element = player_overview.find_element(By.CLASS_NAME, "rating")
                rating_text = rating_element.text


                if not rating_text:
                    continue
                
                if (threshold == 0):
                    pass
                elif (int(rating_text) < threshold):
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
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div/ul/li[3]'))).click() 

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

                if int(element) == 150:
                    WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/button[1]'))).click() 
                time.sleep(1)

            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[1]/div/div/button[2]'))).click() 
            time.sleep(10)
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/nav/button[3]'))).click()


    def getToSBC(self):
        WebDriverWait(self.chromeBrowser, 15).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/nav/button[6]'))
                ).click()
        
        time.sleep(1)

    def dailySBC(self):        
        
        dgu = [
            ["Bronze Challenge", 1, 11],
            ["Silver Challenge", 2, 11]
        ]

        sbcs = {}
        # val 0 is quality, val is num of times sbc can be done, val 2 is num of players
        sbcs["Daily Bronze Upgrade"] = [1,2,1]
        sbcs["Team of the Season Daily Login Upgrade"] = [1,2,1]
        sbcs["Daily Silver Upgrade"] = [2,2,1]

        try:
            for key, value in sbcs.items():
                try:
                    for i in range (0, value[1]):
                        self.getToSBC()
                        h1_element = self.chromeBrowser.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='"+key+"']")
                        div = h1_element.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='"+key+"']/ancestor::*[3]")
                        try:
                            div.click()
                        except:
                            continue
                        try:
                            WebDriverWait(self.chromeBrowser, 2).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/section/div/div[2]/button[3]'))
                                    ).click()
                            WebDriverWait(self.chromeBrowser, 2).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))
                                    ).click()
                        except Exception as e:
                            pass
                        
                        positionsToFill = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-squad-slot-view:not(.ut-squad-slot-view.locked)")
                        for i in range(0, value[2]):
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
                            Position reset
                            '''

                            WebDriverWait(self.chromeBrowser, 5).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[5]/div/div/button'))
                                    ).click()
                                        
                            '''
                            Quality button.
                            '''

                            WebDriverWait(self.chromeBrowser, 5).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[3]/div/div'))
                                    ).click()
                            
                            WebDriverWait(self.chromeBrowser, 5).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[3]/div/ul/li["+str(value[0]+1)+"]"))
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
                        self.openPacks()
                except:
                    pass
        except Exception as e:
            pass
                
        try:
            for i in range(0,4):
                    key = "Daily Gold Upgrade"
                    self.getToSBC()
                    h1_element = self.chromeBrowser.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='"+key+"']")
                    div = h1_element.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='"+key+"']/ancestor::*[3]")
                    try:
                        div.click()
                    except:
                        continue

                    time.sleep(2)
                    sub = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-sbc-challenge-table-row-view:not(.ut-sbc-challenge-table-row-view.complete)")
                    j = 0
                    for i in range(0,2):
                        time.sleep(5)
                        sub = self.chromeBrowser.find_element(By.CSS_SELECTOR, "div.ut-sbc-challenge-table-row-view:not(.ut-sbc-challenge-table-row-view.complete)")
                        sub.click()
                        WebDriverWait(self.chromeBrowser, 5).until(
                                    ec.element_to_be_clickable((
                                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[2]/footer/button'))
                                        ).click()
                        time.sleep(1)
                        
                        try:
                            WebDriverWait(self.chromeBrowser, 2).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/section/div/div[2]/button[3]'))
                                    ).click()
                            WebDriverWait(self.chromeBrowser, 2).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))
                                    ).click()
                        except Exception as e:
                            pass

                        positionsToFill = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-squad-slot-view:not(.ut-squad-slot-view.locked)")
                        for i in range(0, dgu[i][2]):
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

                            WebDriverWait(self.chromeBrowser, 5).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[3]/div/div'))
                                    ).click()
                            
                            text = WebDriverWait(self.chromeBrowser, 5).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, "/html/body/main/section/section/div[1]/h1"))
                                    ).text
                        
                            if text == "Silver Challenge":
                                o = 3
                            elif text == "Bronze Challenge" or text == "TOTS Warm up Daily Login Upgrade":
                                o = 2
                                
                            WebDriverWait(self.chromeBrowser, 5).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[3]/div/ul/li["+str(o)+"]"))
                                    ).click()
                            
                            '''
                            Position reset
                            '''
                            
                            WebDriverWait(self.chromeBrowser, 5).until(
                                ec.element_to_be_clickable((
                                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[5]/div/div/button'))
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
                
                            time.sleep(2)
                            positionsToFill = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-squad-slot-view:not(.ut-squad-slot-view.locked)")
                        j+=1
                        WebDriverWait(self.chromeBrowser, 5).until(
                        ec.element_to_be_clickable((
                            By.XPATH, '/html/body/main/section/section/div[2]/div/div/div/div[2]/button[2]'))
                            ).click()
                        
                        for i in range(0,3):
                            try:
                                WebDriverWait(self.chromeBrowser, 5).until(
                                        ec.element_to_be_clickable((
                                            By.XPATH, '/html/body/div[4]/div/footer/button'))
                                            ).click()
                            except:
                                pass
                        self.openPacks()
        except:
            pass

    def EightyOnePlusPP(self):
        self.getToSBC()
        h1_element = self.chromeBrowser.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='81+ Player Pick']")
        div = h1_element.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='81+ Player Pick']/ancestor::*[3]")
        div.click()
        time.sleep(5)

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
        for i in range(0, 8):
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
    def getToStore(self):
        '''
        Store Button on left hand pane.
        '''
        WebDriverWait(self.chromeBrowser, 5).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/nav/button[4]'))
                ).click()
        
        '''
        Packs.
        '''
        WebDriverWait(self.chromeBrowser, 5).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[3]'))
                ).click()
        
        time.sleep(2)

    def StoreAllInClub(self):
        WebDriverWait(self.chromeBrowser, 20).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[1]/section/header/button[2]'))
                ).click()
        WebDriverWait(self.chromeBrowser, 5).until(
            ec.element_to_be_clickable((
                By.XPATH, '/html/body/div[4]/div/div/button[1]'))
                ).click()
        time.sleep(1)

    def TryDiscardRemainingItems(self):
        try:
            WebDriverWait(self.chromeBrowser, 1).until(
                ec.element_to_be_clickable((
                By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[1]/section/div/button'))
                ).click()
            WebDriverWait(self.chromeBrowser, 1).until(
                ec.element_to_be_clickable((
                By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))
                ).click()
        except:
            pass

    def openPacks(self):
        self.getToStore()
        words = ["bronze", "silver"]
        noDiscard = ["11 Gold Players Pack", "Common Gold Pack"]
        
        try:
            pack_elements = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-store-pack-details-view")
            for pack in pack_elements:
                pack_title = pack.find_element(By.CSS_SELECTOR, "h1.ut-store-pack-details-view--title").text
                if (any(word in pack_title.lower() for word in words)):
                    pack.find_element(By.CSS_SELECTOR, "button.currency.call-to-action").click()
                    self.StoreAllInClub()
                    self.TryDiscardRemainingItems()
                    return
                elif (pack_title in noDiscard):
                    pack.find_element(By.CSS_SELECTOR, "button.currency.call-to-action").click()
                    self.StoreAllInClub()
                    self.TryDiscardRemainingItems()
                    return
                # elif (pack_title in noDiscard):
                #     pack.find_element(By.CSS_SELECTOR, "button.currency.call-to-action").click()
                #     self.StoreAllInClub()
                #     return
        except Exception as e:
            WebDriverWait(self.chromeBrowser, 1).until(
                ec.element_to_be_clickable((
                By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))
                ).click()
            return

    def AutoBidPlayers(self, playerName, max_bn):
        orignal_mbn_price = max_bn
        mbn_price = orignal_mbn_price

        #transfers
        WebDriverWait(self.chromeBrowser, 60).until(ec.presence_of_element_located((By.XPATH, '/html/body/main/section/nav/button[3]'))).click()

        #search the transfer market
        WebDriverWait(self.chromeBrowser, 60).until(ec.presence_of_element_located((By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[2]'))).click()

        #players
        WebDriverWait(self.chromeBrowser, 60).until(ec.presence_of_element_located((By.XPATH, '/html/body/main/section/section/div[2]/div/div[1]/div/button[1]'))).click()
    
        #name
        n = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/input')
        n.click()
        n.send_keys(Keys.CONTROL, 'a')
        n.send_keys(Keys.BACKSPACE)
        n.send_keys(playerName)
        WebDriverWait(self.chromeBrowser, 60).until(ec.presence_of_element_located((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[1]/div/div[2]/ul/button[1]'))).click()

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
        for i in range(0,25):
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[3]/div[2]/button[2]'))).click() #max bid

        
        '''
        Search and allow assets to load.
        '''
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[2]/button[2]'))).click()
        time.sleep(2)

        '''
        Gather all auctions on page and places a bid if the item is worth more than 1000 coins.
        '''
        listed = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data")

        for i in range(0,len(listed)):
            listed[i].click()
            time_text = listed[i].find_element(By.CSS_SELECTOR, "span.time").text
            if not (self.contains_time_words(time_text)):
                return
            try:
                element = self.chromeBrowser.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[1]/div/div[2]/span[2]").text
                if int(element) > (max_bn+500):
                    continue
                price_element = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/div/input')
                price_element.click()
                price_element.send_keys(Keys.CONTROL, 'a')
                price_element.send_keys(Keys.BACKSPACE)
                price_element.send_keys(str(max_bn))
                WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/button[1]'))).click() #bid
                try:
                    WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))).click() #cancel re-bid
                except:
                    pass
            except Exception as e:
                pass

            time.sleep(1) # Apply delay between bids.
        



    def GenericSBC(self, sbc_title, quality, numberOfPlayers, rating_low, rating_high, numberOfRares, rarityMatters):
        self.getToSBC()
        h1_element = self.chromeBrowser.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='"+sbc_title+"']/ancestor::*[3]")
        div = h1_element.find_element(By.XPATH, "//h1[@class='tileTitle' and text()='"+sbc_title+"']/ancestor::*[3]")
        div.click()

        counterToStop = -1

        if (numberOfRares > 0):
            counterToStop = numberOfPlayers - numberOfRares


        time.sleep(5)
        
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
        
        positionsToFill = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.ut-squad-slot-view:not(.ut-squad-slot-view.locked)")
        for i in range(0, numberOfPlayers):
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

            if (i == counterToStop):
                rarity = 3
            else:
                rarity = 2

            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[3]/div/div'))
                    ).click()
            
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[3]/div/ul/li['+str(quality)+']'))
                    ).click()
                        
            WebDriverWait(self.chromeBrowser, 5).until(
                ec.element_to_be_clickable((
                    By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[2]/div[2]/div[5]/div/div/button'))
                    ).click()
                        
            if (rarityMatters):
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
            
            if (i >= counterToStop):
                rating = WebDriverWait(self.chromeBrowser, 5).until(
                    ec.element_to_be_clickable((
                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[2]/div/div/div/div[1]/ul/li/div/div[1]/div[1]/div[4]/div[2]/div[1]'))
                        ).text                
                if (int(rating) > rating_high):
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
        coinTotal = self.chromeBrowser.find_element(By.CSS_SELECTOR, "div.view-navbar-currency-coins").text
        
        self.logMessageToServer(str(coinTotal), True)

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

        try:
            ListSection = self.find_grandparent_element("h2", "Won Items")

            m = ListSection.find_elements(By.CSS_SELECTOR, "li[class*='has-substring']")

            for item in m:
                item.click()
                WebDriverWait(self.chromeBrowser, 10).until(
                    ec.element_to_be_clickable((
                        By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[3]/button[6]'))
                        ).click()
        except:
            pass

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
                    return
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
                    return
            
            time.sleep(1)

        self.logMessageToServer("All items have been added to the transfer list.", False)

    def relistItemsOnly(self):
        self.logMessageToServer("Items relist only has begun.", False)
        time.sleep(5) # Allow web application to load assets.

        self.clearSold()

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
        
        time.sleep(30)

        self.logMessageToServer("All items have been relisted only.", False)
        self.relistAndUpdatePrice()

    def clearSold(self):
        try:
            for item in self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data.won"):
                item.click()
                time.sleep(2)
                price = item.find_elements(By.CSS_SELECTOR, "span.currency-coins.value")
                price = (price.pop()).text
                price = str(int(price.replace(",", "")))

                name = item.find_element(By.CSS_SELECTOR, "div.name").text
                
                try:
                    type_parent = self.chromeBrowser.find_element(By.CSS_SELECTOR, "div.tns-item.tns-slide-active")
                    desc = type_parent.find_element(By.CSS_SELECTOR, "div.clubView").text  
                except:
                    desc = ""


                    
                data = {
                    'item_name': name + " " + desc,
                    'sold_price': price
                }
                requests.get(self.price_url, params=data)
        except:
            pass
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

    def find_grandparent_element(self, tag_name, text):
        element = self.chromeBrowser.find_element(By.XPATH, f"//{tag_name}[contains(text(), '{text}')]")
        grandparent_element = element.find_element(By.XPATH, "..").find_element(By.XPATH, "..")
        return grandparent_element

    def compare_price(self):
        right_pane = self.chromeBrowser.find_element(By.CSS_SELECTOR, "div.DetailPanel")
        span_element = right_pane.find_element(By.XPATH, "//span[contains(text(), 'Compare Price')]")
        parent_element = span_element.find_element(By.XPATH, "..").click()
        time.sleep(2)
        return parent_element
    

    def RCItem(self, s):
        previous_name = ""
        previous_type = ""
        same_count = 0
    
        while (1):
            lowest_price = None
            list_price = 0

            self.clearSold()
            
            ListSection = self.find_grandparent_element("h2", s)
            try:
                item = ListSection.find_element(By.CSS_SELECTOR, "li.listFUTItem")
            except:
                break

            item.click()
            self.compare_price()

            try:
                name_text = item.find_element(By.CSS_SELECTOR, "div.name").text
                
                try:
                    type_parent = self.chromeBrowser.find_element(By.CSS_SELECTOR, "div.tns-item.tns-slide-active")
                    desc_text = type_parent.find_element(By.CSS_SELECTOR, "div.clubView").text  
                except:
                    desc_text = ""

                combined = name_text + " " + desc_text
            except:
                pass

            lowest_price = self.getLowestPrice(1, combined)   
            
            if lowest_price == None or lowest_price == 0:
                lowest_price = 5000

            lowest_price -= int(lowest_price) * 0.10
            list_price = int(lowest_price)

            item.click() # Exit Compare Pane

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

            highlighted_item = self.chromeBrowser.find_element(By.CSS_SELECTOR, 'div.ut-navigation-container-view--content')
            name = highlighted_item.find_element(By.CSS_SELECTOR, 'div.name').text  
            type = highlighted_item.find_element(By.CSS_SELECTOR, 'div.clubRow').text  

            if (name == previous_name):
                same_count += 1
            else:
                same_count = 0
            
            if same_count == 3:
                return

            WebDriverWait(self.chromeBrowser, 2).until(ec.element_to_be_clickable((
                By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div/div/div[2]/div[2]/div[2]/button"))
            ).click() # Confirm Price.

            previous_name = name
            previous_type = type 

            time.sleep(2)

    def relistAndUpdatePrice(self):
        self.logMessageToServer("Items relist and reprice has begun.", False)

        time.sleep(5) # Allow web application to load assets.
        
        self.clearSold()

        self.RCItem("Unsold Items")
        self.RCItem("Available Items")



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
        if not self.isReprice:
            self.relistItemsOnly()

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

        while (1):
            listed = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data")
            for i in range(0,len(listed)):
                listed[i].click()
                type_parent = self.chromeBrowser.find_element(By.CSS_SELECTOR, "div.tns-item.tns-slide-active")

                time_text = listed[i].find_element(By.CSS_SELECTOR, "span.time").text
                name_text = listed[i].find_element(By.CSS_SELECTOR, "div.name").text
                type_text = type_parent.find_element(By.CSS_SELECTOR, "div.clubRow").text
                combined = name_text + " " + type_text

                if not (self.contains_time_words(time_text)):
                    return

                try:
                    self.compare_price()
                    lowest_price = self.getLowestPrice(0, combined)   

                    listed[i].click()
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
            list = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.paginated-item-list.ut-pinned-list")[0]
            listed = list.find_element(By.CSS_SELECTOR, "button.flat.pagination.next")
            if (listed.is_displayed()):
                listed.click()
                time.sleep(2)
            else:
                break


    def buyClubItemsGold(self, isBadges):
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
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div/ul/li[4]'))).click() 
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[4]/div/div'))).click()
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[4]/div/ul/li[3]'))).click()
        if isBadges:
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[5]/div/div'))).click()
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[5]/div/ul/li[3]'))).click()

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
        for i in range(0,8):
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[3]/div[2]/button[2]'))).click() #max bid

        for i in range(0,18):
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[2]/div[5]/div[2]/button[2]'))).click() #min buy now
        
        '''
        Search and allow assets to load.
        '''
        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[2]/button[2]'))).click()
        time.sleep(2)



        for i in range(0,4):
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[1]/div/div/button[2]'))).click() 
            time.sleep(0.5)

        '''
        Gather all auctions on page and places a bid if the item is worth more than 1000 coins.
        '''
        listed = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data")

        for i in range(0,len(listed)-1):
            listed[i].click()
            time_text = listed[i].find_element(By.CSS_SELECTOR, "span.time").text
            if not (self.contains_time_words(time_text)):
                return

            try:
                self.compare_price()
                lowest_price = self.getLowestPrice(0)   

                listed[i].click()

                WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[1]/button'))).click() #back
                time.sleep(2)
                if lowest_price > 1000:
                    price_element = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/div/input')
                    price_element.click()
                    price_element.send_keys(Keys.CONTROL, 'a')
                    price_element.send_keys(Keys.BACKSPACE)
                    bid_price = lowest_price * 0.1
                    if (bid_price < 500):
                        bid_price = 500
                    price_element.send_keys(str(bid_price))
                    WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/button[1]'))).click() #bid
                    try:
                        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))).click() #cancel re-bid
                    except:
                        pass
            except:
                pass

    def compareItems(self):
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

        return lowest_price
    
    def compareItemsAlt(self):
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
            buy_now_prices.remove(lowest_price)
            if (len(buy_now_prices) > 0):
                lowest_price_second = min(buy_now_prices)
            else:
                return lowest_price

        if (lowest_price_second - lowest_price) > 1000:
            return lowest_price_second

        
        return lowest_price
    
    def bidManagerLeague(self, league):
        self.chromeBrowser.find_element(By.CSS_SELECTOR, "button.ut-tab-bar-item.icon-club").click()
        time.sleep(2)
        self.chromeBrowser.find_element(By.CSS_SELECTOR, "div[class*=consumables-tile]").click()
        time.sleep(2)
        self.chromeBrowser.find_element(By.CSS_SELECTOR, "div[class*=managerLeague-tile]").click()
        time.sleep(2)
        list = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-substring")

        for item in list:
            item.click()
            time.sleep(1)

            type_parent = self.chromeBrowser.find_element(By.CSS_SELECTOR, "div.tns-item.tns-slide-active").text
            
            if (league in type_parent):
                self.compare_price()
                time.sleep(1)
                while(1):
                    listOfItems = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.paginated-item-list.ut-pinned-list")[1]
                    items = listOfItems.find_elements(By.CSS_SELECTOR, "li[class*=listFUTItem]")

                    try:
                        for each in items:
                            
                            time_text = each.find_element(By.CSS_SELECTOR, "span.time").text

                            if not (self.contains_time_words(time_text)):
                                return
            
                            minBidPriceParent = each.find_element(By.CSS_SELECTOR, "div.auctionStartPrice.auctionValue")
                            minBidPrice = minBidPriceParent.find_element(By.CSS_SELECTOR, "span.currency-coins.value").text.replace(",", "")

                            currentBidParent = each.find_elements(By.CSS_SELECTOR, "div.auctionValue")[1]
                            currentBid = currentBidParent.find_element(By.CSS_SELECTOR, "span.currency-coins.value").text.replace(",", "")

                            if (currentBid == "---"):
                                currentBid = 0
                            
                            print(minBidPrice)
                            if (int(minBidPrice) <= 500 and int(currentBid) <= 500):
                                minBidPriceParent.click()
                                time.sleep(1)

                                maxBid = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div/section/div[2]/section/div/div/div[2]/div[2]/div/input')
                                maxBid.click()
                                maxBid.send_keys(Keys.CONTROL, 'a')
                                maxBid.send_keys(Keys.BACKSPACE)
                                maxBid.send_keys("500")

                                self.chromeBrowser.find_element(By.CSS_SELECTOR, "button.btn-standard.call-to-action.bidButton").click()
                                time.sleep(1)

                                try:
                                    self.chromeBrowser.find_element(By.XPATH, "/html/body/div[4]/section/div/div/button[1]").click()
                                except:
                                    pass

                                self.chromeBrowser.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/section/div[1]/button").click()

                                time.sleep(1)

                    except Exception as e:
                        print(e)

                    nextbtn = listOfItems.find_element(By.CSS_SELECTOR, "button.flat.pagination.next")
                    if (nextbtn.is_displayed()):
                        nextbtn.click()
                        time.sleep(2)
                





        while 1:
            pass
    
    def getLowestPrice(self, isAlt, combined):
        try:
            lowest_price = 0
            while (1):
                if (isAlt):
                    l = self.compareItemsAlt()
                else:
                    l = self.compareItems()
                    
            
                if ((l < lowest_price) or (lowest_price == 0)):
                    lowest_price = l
                    list = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "div.paginated-item-list.ut-pinned-list")[1]
                    listed = list.find_element(By.CSS_SELECTOR, "button.flat.pagination.next")
                    if (listed.is_displayed()):
                        listed.click()
                        time.sleep(2)
                    
                    data = {
                        'name': combined,
                        'price':lowest_price
                    }

                    requests.get("http://192.168.1.210?write_seen=1", params=data)
                else:
                    break
        except Exception as e:
            print(e)

        if lowest_price == 0:
            lowest_price = 5000


        return lowest_price

    def buyPitchCosmetics(self, type):
        '''
        Navigate and apply filters:
            1. Transfers
            2. Search the Transfer Market
            3. Club Items
            4. Pitch
            5. Pitch Line Paint
        '''
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/nav/button[3]'))).click()

        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[2]/div[2]'))).click() #Transfer Market
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[1]/div/button[3]'))).click() #Club Items

        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[2]/button[1]'))).click() #Reset

        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div/div'))).click() 
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div/ul/li[4]'))).click() #Pitch
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[5]/div/div'))).click() 
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, "/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[5]/div/ul/li["+str(type)+"]"))).click() #Pitch Line Paint

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
            listed = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data")
            try:
                listed[i].click()
            except:
                continue

            type_parent = self.chromeBrowser.find_element(By.CSS_SELECTOR, "div.tns-item.tns-slide-active")

            time_text = listed[i].find_element(By.CSS_SELECTOR, "span.time").text
            name_text = listed[i].find_element(By.CSS_SELECTOR, "div.name").text
            type_text = type_parent.find_element(By.CSS_SELECTOR, "div.clubRow").text

            combined = name_text + " " + type_text

            if (combined in self.blacklist):
                continue
            else:
                print(name_text)

            if not (self.contains_time_words(time_text)):
                return

            try:
                WebDriverWait(self.chromeBrowser, 10).until(ec.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Compare Price')]]"))).click()
            except:
                continue
            try:
                time.sleep(2)

                lowest_price = self.getLowestPrice(0, combined)

                WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[1]/button'))).click() #back
                time.sleep(2)
                if lowest_price > 2000:
                    price_element = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/div/input')
                    price_element.click()
                    price_element.send_keys(Keys.CONTROL, 'a')
                    price_element.send_keys(Keys.BACKSPACE)
                    sale_price = lowest_price * 0.1
                    if (sale_price > 500):
                        sale_price = 500
                    price_element.send_keys(str(sale_price))
                    WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/button[1]'))).click() #bid
                    try:
                        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))).click() #cancel re-bid
                    except:
                        pass
            except:
                pass

            time.sleep(5) # Apply delay between bids.

    def buyStadiumCosmetics(self, type):
        '''
        Navigate and apply filters:
            1. Transfers
            2. Search the Transfer Market
            3. Club Items
            4. Structure
            5. Seat Paint
        '''
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/nav/button[3]'))).click()

        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[2]/div[2]'))).click() #Transfer Market
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[1]/div/button[3]'))).click() #Club Items

        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[2]/button[1]'))).click() #Reset

        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div/div'))).click() 
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[2]/div/ul/li[2]'))).click() #Structure
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[5]/div/div'))).click() 
        WebDriverWait(self.chromeBrowser, 15).until(ec.element_to_be_clickable((By.XPATH, "/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[5]/div/ul/li["+str(type)+"]"))).click() #Seat Paint

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
            listed = self.chromeBrowser.find_elements(By.CSS_SELECTOR, "li.listFUTItem.has-auction-data")
            listed[i].click()
            time.sleep(2)

            type_parent = self.chromeBrowser.find_element(By.CSS_SELECTOR, "div.tns-item.tns-slide-active")

            time_text = listed[i].find_element(By.CSS_SELECTOR, "span.time").text
            name_text = listed[i].find_element(By.CSS_SELECTOR, "div.name").text
            type_text = type_parent.find_element(By.CSS_SELECTOR, "div.clubRow").text

            combined = name_text + " " + type_text

            if (combined in self.blacklist):
                continue

            if not (self.contains_time_words(time_text)):
                return

            try:
                WebDriverWait(self.chromeBrowser, 10).until(ec.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Compare Price')]]"))).click()
            except:
                continue
            try:
                time.sleep(2)

                lowest_price = self.getLowestPrice(0, combined)

                WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section/div[1]/button'))).click() #back
                time.sleep(2)
                if lowest_price > 1000:
                    price_element = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/div/input')
                    price_element.click()
                    price_element.send_keys(Keys.CONTROL, 'a')
                    price_element.send_keys(Keys.BACKSPACE)
                    sale_price = lowest_price * 0.2
                    if (sale_price > 500):
                        sale_price = 500
                    price_element.send_keys(str(sale_price))
                    WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/button[1]'))).click() #bid
                    try:
                        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))).click() #cancel re-bid
                    except:
                        pass
            except Exception as e:
                print(e)
                pass

    def buyManagers(self, nationNum):
            '''
            Navigate and apply filters:
                1. Transfers
                2. Search the Transfer Market
                3. Managers
                4. Quality
                5. Bronze
            '''
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/nav/button[3]'))).click()
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/div[2]/div[2]'))).click() 
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[2]/button[1]'))).click() 
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[1]/div/button[2]'))).click() 
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div/div'))).click()
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div/ul/li[2]'))).click() 
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[4]/div/div'))).click() 
            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, "/html/body/main/section/section/div[2]/div/div[2]/div/div[1]/div[1]/div[4]/div/ul/li["+str(nationNum)+"]"))).click() 

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
            for i in range(0,8):
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

            for i in range(0,3):
                listed[i].click()
                time_text = listed[i].find_element(By.CSS_SELECTOR, "span.time").text
                if not (self.contains_time_words(time_text)):
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
                    if lowest_price > 2000:
                        price_element = self.chromeBrowser.find_element("xpath", '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/div/input')
                        price_element.click()
                        price_element.send_keys(Keys.CONTROL, 'a')
                        price_element.send_keys(Keys.BACKSPACE)
                        price_element.send_keys(str(500))
                        WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[2]/button[1]'))).click() #bid
                        try:
                            WebDriverWait(self.chromeBrowser, 5).until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[4]/section/div/div/button[1]'))).click() #cancel re-bid
                        except:
                            pass
                except:
                    pass

                time.sleep(2) # Apply delay between bids.


            
