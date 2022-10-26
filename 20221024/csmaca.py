import numpy as np
import random

_n=50 # number of nodes
_simTime=500 # sec

rate=11 # 11, 5.5, 2 or 1 Mbps (BEB 802.11傳送速度)
_cwmin=32 # 挑選值範圍，若發生碰撞將會變動
_cwmax=1024 # 若發生碰撞挑選值最多只增加至1024
rtsmode=0 #0: data->ack; 1:rts->cts->data->ack

SIFS=10  # short interframe space  單位：ms(10^-6s)
DIFS=50  # distributed interframe space 確保ACK封包正確回傳
EIFS=SIFS+DIFS+192+112  # 碰撞發生封包重送時間
SLOT=20  # 亂數*時間單位
M=1000000  # 封包大小

_pktSize=1000 # bytes
stat_succ=0  # 成功傳送次數
stat_coll=0  # 碰撞發生次數
stat_pkts=np.zeros(_n)  # 統計節點發送多少封包
cw=np.zeros(_n)
bo=np.zeros(_n)  # badoff 亂數

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
        if bo[i]==min:
            count+=1

    return count

def subMinBoFromAll(min,count):
    global _cwmin,_cwmax
    for i in range(0,_n):  # 所有節點
        if bo[i]<min:
            print("<Error> min=",min," bo=",bo[i])
            exit(1)

        if bo[i]>min:
            bo[i]-=min  # 時間推進

        elif bo[i]==min:
            if count==1:
                cw[i]=_cwmin
                bo[i] = random.randint(0, _cwmax) % cw[i]  # 直接取新亂數
            elif count>1:
                if cw[i]<_cwmax:
                    cw[i]*=2  # min*2後取新亂數
                else:
                    cw[i]=_cwmax
                bo[i] = random.randint(0, _cwmax) % cw[i]
            else:
                print("<Error> count=",count)
                exit(1)

def setStats(min,index,count):
    global stat_succ,stat_coll
    if count==1:
        stat_pkts[index]+=1  # 節點成功傳遞量
        stat_succ+=1  # 總成功傳遞量
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

    if count==1:  # 傳送成功
        now+=DIFS/M  # 等待時間
        now+=min*SLOT/M  # 取亂數
        now+=Tdata()/M  # 傳送data
        now+=SIFS/M  # SIFS
        now+=Tack()/M  # 回傳ACK
    elif count>1:  # 傳送失敗
      if rtsmode==1:
          now+=EIFS/M
          now+=min*SLOT/M
      else:
          now+=EIFS/M
          now+=min*SLOT/M
          now+=Tdata()/M
    else:
          print("<Error> count=", count)
          exit(1)

def resolve():
    index=getMinBoAllStationsIndex()  # 一次搜尋各亂數之最小值
    min=bo[index]  # 
    count=getCountMinBoAllStations(min)  # 統計最小亂數總數量

    setNow(min, count)  # 時間推進
    setStats(min, index, count)
    subMinBoFromAll(min, count)

def printStats():
    print("\nGeneral Statistics\n")
    print("-"*50)

    numPkts=0
    for i in range(0,_n):
        numPkts+=stat_pkts[i]  # 系統總計成功傳遞量
    print("Total num of packets:", numPkts)  # 封包量
    print("Collision rate:", stat_coll/(stat_succ+stat_coll)*100, "%")  # 失敗率
    print("Aggregate Throughput:", numPkts*(_pktSize*8.0)/now)  # 吞吐量（單位時間的傳送量）

def main():
    global now, _simTime
    random.seed(1)

    init_bo()  # 節點初始化
    while now < _simTime:
        resolve()  
    printStats()

main()