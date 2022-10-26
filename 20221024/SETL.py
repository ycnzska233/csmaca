import numpy as np
import random

_n=150 # number of nodes
_simTime=200 # sec

rate=11 # 11, 5.5, 2 or 1 Mbps
_cwmin=32
_cwmax=1024
rtsmode=0 #0: data->ack; 1:rts->cts->data->ack

SIFS=10
DIFS=50
EIFS=SIFS+DIFS+192+112
SLOT=20
M=1000000

_pktSize=1000 # bytes
stat_succ=0
stat_coll=0
stat_pkts=np.zeros(_n)
cw=np.zeros(_n)
bo=np.zeros(_n)

now=0.0

def init_bo():
    for i in range(0,_n):
        cw[i]=_cwmin
        bo[i]=random.randint(0,_cwmax)%cw[i]
        #print("cw[",i,"]=",cw[i]," bo[",i,"]=",bo[i])

def Trts():
    time=192+(20*8)/1
    return time

def Tcts():
    time=192+(14*8)/1
    return time

def Tdata():
    global rate
    time=192+((_pktSize+28)*8.0)/rate
    return time

def Tack():
    time=192+(14*8.0)/1
    return time

def getMinBoAllStationsIndex():
    index=0
    min=bo[index]
    for i in range(0,_n):
        if bo[i]<min:
            index=i
            min=bo[index]

    return index

def getCountMinBoAllStations(min):
    count=0
    for i in range(0,_n):
        if(bo[i]==min):
            count+=1

    return count

def subMinBoFromAll(min,count):
    global _cwmin,_cwmax
    for i in range(0,_n):
        if bo[i]<min:
            print("<Error> min=",min," bo=",bo[i])
            exit(1)

        if(bo[i]>min):
            bo[i]-=min
        elif bo[i]==min:
            if count==1:
                if cw[i]<=512 and cw[i]>32:
                   cw[i]/=2
                elif cw[i]>512:
                        cw[i]-=32
                bo[i] = random.randint(0, _cwmax) % cw[i]
            elif count>1:
                if cw[i]<_cwmax and cw[i]>=512:
                    cw[i]+=2
                elif cw[i]==_cwmax:
                     cw[i]=_cwmax
                else:
                     cw[i]*=2
                bo[i] = random.randint(0, _cwmax) % cw[i]
            else:
                print("<Error> count=",count)
                exit(1)

def setStats(min,index,count):
    global stat_succ,stat_coll
    if count==1:
        stat_pkts[index]+=1
        stat_succ+=1
    else:
        stat_coll+=1
        for i in range(0,_n):
            if bo[i]<min:
                print("<Error> min=", min, " bo=", bo[i])
                exit(1)
            #elif bo[i]==min:
            #    print("Collision with min=", min)

def setNow(min,count):
    global M, now, SIFS, DIFS, EIFS, SLOT
    if rtsmode==1:
        now+=Trts()/M;

    if count==1:
        now+=DIFS/M
        now+=min*SLOT/M
        now+=Tdata()/M
        now+=SIFS/M
        now+=Tack()/M
    elif count>1:
          now+=DIFS/M          
          now+=min*SLOT/M
          now+=Tdata()/M
          now+=EIFS/M
    else:
          print("<Error> count=", count)
          exit(1)

def resolve():
    index=getMinBoAllStationsIndex()
    min=bo[index]
    count=getCountMinBoAllStations(min)

    setNow(min, count)
    setStats(min, index, count)
    subMinBoFromAll(min, count)

def printStats():
    print("\nGeneral Statistics\n")
    print("-"*50)

    numPkts=0
    for i in range(0,_n):
        numPkts+=stat_pkts[i]
    print("Node:", _n)
    print("Total num of packets:", numPkts)
    print("Collision rate:", stat_coll/(stat_succ+stat_coll)*100, "%")
    print("Aggregate Throughput:", numPkts*(_pktSize*8.0)/now)

def main():
    global now, _simTime
    random.seed(1)

    init_bo()
    while now < _simTime:
        resolve()
    printStats()

main()
