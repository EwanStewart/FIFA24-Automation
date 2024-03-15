# Ewan Stewart, 2024
# FC 24 automation script to relist and adjust prices of club items.

import sys
from WebApplication import WebApplication
import multiprocessing
import time

def main():
    isDebug = True
    isShutdown = False

    if (len(sys.argv) > 1):
        isDebug = sys.argv[1]
        isShutdown = sys.argv[2]
        
    SeleniumApplication = WebApplication(isDebug, isShutdown)
    
    while (1):
        # inp = input('waiting for key press\n')
        # try:
            # if (str(inp) == 'q'):
                # seleniumapplication.commongoldbids(1)
            # elif (str(inp) == 'w'):
                # seleniumapplication.gettosbc()
                # seleniumapplication.eightyonepluspp()
        # except:
            # continue
        SeleniumApplication.scanClub()
        SeleniumApplication.EightyThreeTimes10()
        # try:
            # SeleniumApplication.getToSBC()
            # SeleniumApplication.EightyOnePlusPP()
        # except:
            # pass

    #SeleniumApplication.exitApplication()

main()
