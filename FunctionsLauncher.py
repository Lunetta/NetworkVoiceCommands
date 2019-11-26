import os
import re
import socket
import argparse
from NetworkClassFunctions import Host



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("iphost", type=str, help="host specification ip")#insert function
    args = parser.parse_args()
    ip_prov=args.iphost
    checkip=re.search('[a-zA-Z]',ip_prov)
    #insert mapping functions
    if checkip:
        try:
            ip=ip=socket.gethostbyname(ip_prov)
            myHost=Host(ip)
            myHost.latency()# or ping
        except:
            print("Host not find")

    else:
        ip=ip_prov
        myHost=Host(ip)
        myHost.latency()# or ping 
