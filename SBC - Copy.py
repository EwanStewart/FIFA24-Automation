# Ewan Stewart, 2024
# FC 24 automation script to relist and adjust prices of club items.

import sys
from WebApplication import *

PSU = SBC("Premium Silver Upgrade", SILVER_QUALITY, 11, SILVER_LOW, SILVER_HIGH, 0, False)
EightOnePlusPP = SBC("81+ Player Pick", GOLD_QUALITY, 8, GOLD_LOW, GOLD_HIGH, 1, True)
EightyPlusPP = SBC("80+ Player Pick", GOLD_QUALITY, 6, GOLD_LOW, GOLD_HIGH, 1, True)
EightyTriplePack = SBC("80+ Triple Upgrade", GOLD_QUALITY, 11, GOLD_LOW, GOLD_HIGH, 1, False)

def main():
    isDebug = False
    isShutdown = False

    if (len(sys.argv) > 1):
        isDebug = sys.argv[1]
        isShutdown = sys.argv[2]
        
    SeleniumApplication = WebApplication(isDebug, isShutdown, False)

    while (1):
        SeleniumApplication.GenericSBC(EightyTriplePack.title, EightyTriplePack.quality, EightyTriplePack.numberOfPlayers, EightyTriplePack.low, EightyTriplePack.high, EightyTriplePack.numberOfRares, EightyTriplePack.rarityMatters)
        

    # try:
    #     SeleniumApplication.AutoBidPlayers("Ouleymata Sarr", 1500)
    # except Exception as e:
    #     print(e)
    #     pass

main()
