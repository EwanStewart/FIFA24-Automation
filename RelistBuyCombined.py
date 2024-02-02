# Ewan Stewart, 2024
# FC 24 automation script to relist and adjust prices of club items.

import sys
from WebApplication import WebApplication

def main():
    isDebug = False
    isShutdown = False

    if (len(sys.argv) > 1):
        isDebug = sys.argv[1]
        isShutdown = sys.argv[2]
        
    SeleniumApplication = WebApplication(isDebug, isShutdown)

    try:
        SeleniumApplication.sendWonItemsToTransferList()
        SeleniumApplication.getToTransferList()
        SeleniumApplication.relistOrReprice()
        SeleniumApplication.buyClubItems(False)
        SeleniumApplication.buyClubItems(True)
    except:
        pass

    SeleniumApplication.exitApplication()

main()