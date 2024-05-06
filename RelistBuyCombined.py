# Ewan Stewart, 2024
# FC 24 automation script to relist and adjust prices of club items.

import sys
from WebApplication import *
import multiprocessing
import time

SWEDEN = 146
COLUMBIA = 39
POLAND = 126
JAPAN = 86

PSU = SBC("Premium Silver Upgrade", SILVER_QUALITY, 11, SILVER_LOW, SILVER_HIGH, 0, False)


def main():
    isDebug = False
    isShutdown = True

    if (len(sys.argv) > 1):
        isDebug = sys.argv[1]
        isShutdown = sys.argv[2]
        
    SeleniumApplication = WebApplication(isDebug, isShutdown, True)
    
    try:    
        try:
            SeleniumApplication.dailySBC()
        except Exception as e:
            pass
          
        try:
            SeleniumApplication.sendWonItemsToTransferList()
        except:
            time.sleep(20)
            pass

        for i in range(0,5):
            try:
                SeleniumApplication.getToTransferList()
                SeleniumApplication.relistOrReprice()
                SeleniumApplication.sendWonItemsToTransferList()
            except Exception as e:
                print(e)
                time.sleep(20)
                pass        
            
        try:
            SeleniumApplication.buyClubItems(False)
        except Exception as e:
            pass
        try:
            SeleniumApplication.buyClubItems(True)
        except:
            pass


        try:
            SeleniumApplication.buyStadiumCosmetics(SEAT_PAINT)
        except Exception as e:
            pass
    except:
        pass

    SeleniumApplication.exitApplication()

main()
