import os
import subprocess


#FUNCTION DEFINITION
#############################################
def latency_calculator(response):
    response=response.replace('\\r\\n','')
    mystructure=response.split('TTL')
    myvector=mystructure[len(mystructure)-1]
    myindex=myvector.find('ms')
    for i in range(0,2):
        print(myvector[myindex+1:])
        index=myvector[myindex+1:].find('ms')
        myindex=index+myindex+1
    index=myindex
    myrange=[index-1,index-2,index-3,index-4]
    latency=''
    control=0
    for i in myrange:
        if myvector[i]=='=':
            control=1
            i=myrange[len(myrange)-1]
        else:
            app=myvector[i]
            latency=app+latency
            
    if control==1:
        return(latency)
    else:
        latency='>='+latency
        return(latency)
    
    
#CLASS DEFINITION
#############################################
class Host:
    def __init__(self, ip):
        self.ip=ip
        
    #Method definition    
    def ping(self):
        response = os.system("ping " + self.ip)  
        if response == 0:
            print("Host "+ self.ip + " is UP")
        else:
            print ("Host "+ self.ip + " is DOWN")


    def latency(self):
        response1=os.system("ping " + self.ip)  
        if response1 == 0:
            response = subprocess.check_output(["ping ",self.ip])
            lat=latency_calculator(str(response))
            print("Host "+ self.ip + " is UP with a average latency of "+ lat +"ms (Calculated on 4 packets)")
        else:
            print ("Host "+ self.ip + " is DOWN")
    
