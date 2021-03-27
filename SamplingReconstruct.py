# import torch
import random
import numpy as np

class SamplingReconstruct():
    # 600,0.5,X
    def __init__(self,machine_num,samplingrate,channel_num):
        self.machine_num=machine_num
        self.samplingrate=samplingrate
        self.channel_num=channel_num
        self.mem=np.zeros((machine_num,channel_num),dtype=float)

    # output size: machiennum
    def sampling(self):
        collect_decision = np.zeros(self.machine_num,dtype=float)
        for k in range(self.machine_num):
            if random.random() < self.samplingrate:
                collect_decision[k]=1
            else:
                collect_decision[k]=0
        return collect_decision

    # input size：(collectnum*channel), machine_num
    # output size: (machine_num*channel),machine_num
    def resizedata(self,collectdata,decision):
        # print(collectdata)
        # print("",np.array(collectdata).shape)
        collecteddata=np.zeros((self.machine_num,self.channel_num),dtype=float)
        for i in range(self.machine_num):
            for j in range(self.channel_num):
                collecteddata[i][j]=float(collectdata[i][j])

        collectnum=sum(decision)
        resizedata=np.zeros((self.machine_num,self.channel_num),dtype=float)
        j=0
        for i in range(self.machine_num):
            if(decision[i]==1):
                resizedata[i]=collecteddata[j]
                j+=1
            else:
                resizedata[i]=[0 for i in range(self.channel_num)]
        return resizedata
    
    # input size: (machinenum*channelnum),machien_num
    # output size: machiennum * channelnum
    def reconstruct(self,collecteddata,decision):
        resizeddata=self.resizedata(collecteddata,decision)
        self.updatemem(resizeddata,decision)
        return self.mem.copy()

    def updatemem(self,resizededdata,decision):
        for k in range(self.machine_num): # 准备下一时刻的 mem
            if decision[k]==1:
                self.mem[k] = resizededdata[k].copy()