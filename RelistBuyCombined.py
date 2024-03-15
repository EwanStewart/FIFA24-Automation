# Ewan Stewart, 2024
# FC 24 automation script to relist and adjust prices of club items.

import sys
from WebApplication import WebApplication
import multiprocessing
import time

def main():
    isDebug = True
    isShutdown = True

    if (len(sys.argv) > 1):
        isDebug = sys.argv[1]
        isShutdown = sys.argv[2]
        
    SeleniumApplication = WebApplication(isDebug, isShutdown)
    
    try:
        try:
            SeleniumApplication.sendWonItemsToTransferList()
        except:
            pass
        try:
            SeleniumApplication.getToTransferList()
            SeleniumApplication.relistOrReprice()
        except:
            time.sleep(20)
            pass
        try:
            SeleniumApplication.buyClubItems(False)
        except Exception as e:
            print(e)
            pass
        try:
            SeleniumApplication.buyClubItems(True)
        except:
            pass
        try:
            if (SeleniumApplication.isReprice):
                time.sleep(10)
                SeleniumApplication.commonGoldBids(True)      
            while (1):  
                SeleniumApplication.getToSBC()
                SeleniumApplication.EightyOnePlusPP()
        except Exception as e:
            print(e)
            pass
    except:
        pass

    SeleniumApplication.exitApplication()

main()
