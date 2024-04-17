# Ewan Stewart, 2024
# FC 24 automation script to relist and adjust prices of club items.

import sys
from WebApplication import *

PSU = SBC("Premium Silver Upgrade", SILVER_QUALITY, 11, SILVER_LOW, SILVER_HIGH, 0, False)
EightOnePlusPP = SBC("81+ Player Pick", GOLD_QUALITY, 8, GOLD_LOW, GOLD_HIGH, 1, True)

def main():
    isDebug = False
    isShutdown = False
    counter = 0
    openCounter = 0

    if (len(sys.argv) > 1):
        isDebug = sys.argv[1]
        isShutdown = sys.argv[2]
        
    SeleniumApplication = WebApplication(isDebug, isShutdown, False)

    while (1):
        try:
            while (1):
                #SeleniumApplication.GenericSBC(PSU.title, PSU.quality, PSU.numberOfPlayers, PSU.low, PSU.high, PSU.numberOfRares, PSU.rarityMatters)
                SeleniumApplication.GenericSBC(EightOnePlusPP.title, EightOnePlusPP.quality, EightOnePlusPP.numberOfPlayers, EightOnePlusPP.low, EightOnePlusPP.high, EightOnePlusPP.numberOfRares, EightOnePlusPP.rarityMatters)
        except:
            pass    
            SeleniumApplication.openPacks()
            SeleniumApplication.openPacks()
    try:
        while (1):
            
            SeleniumApplication.commonGoldBids(1)

            counter += 1

            time.sleep(180)

            SeleniumApplication.sendWonItemsToTransferList()

            if counter == 3:
                SeleniumApplication.exitApplication()
                return
            

    except Exception as e:
        print(e)
        pass

while (1):
    main()
