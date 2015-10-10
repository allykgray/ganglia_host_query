import urllib
import csv
import numpy as np
import json
hostIP=""
teamname=[]
publicIP=[]
softlayer='-static.reverse.softlayer.com'    
f = open('devices.csv', 'rb')
try:
    reader = csv.reader(f)
    for row in reader:
        teamname.append(row[0])
        publicIP.append(row[3])
finally:
    f.close()
    
time='week'
gpus=0,1,2,3
params=list(['100.0&m=cpu_idle','1859.004&m=disk_total'])#,'0&m=gpu'+gpus[0]+'_util'
params2=list(['CPU+Idle','Total+Disk+Space'])#,'gpu'+gpus[0]+'+GPU+Utilization'

for j in range(len(gpus)):
    params.append('0&m=gpu'+str(gpus[j])+'_util')
    params2.append('gpu'+str(gpus[j])+'+GPU+Utilization')
#target = open('output.txt', 'w')
HostSummary=[]
URLLIST=[]
host_cpu_usage=[]
for i in range(len(publicIP)-1):
    for j in range(len(params)):
        URLLIST.append('http://'+hostIP+'/ganglia/graph.php?r='+time+'&z=xlarge&c=imagenet_cluster&h='+publicIP[i+1]+softlayer+'&jr=&js=&v='+params[j]+'&vl=%25&ti='+params2[j]+'&json=1')
for m in range(len(teamname)-1):
    ##CPU Utilization        
    html = urllib.urlopen(URLLIST[(6*m)]).read()   
    data = json.loads(html)[0]
    cpu_usage=(data['datapoints'])
    cpu_usage=np.array(cpu_usage,dtype=np.float)[:,0]
    cpu_usage=cpu_usage[~np.isnan(cpu_usage)]
    temp=np.float(len(cpu_usage[cpu_usage<98.5]))
    host_cpu_usage=temp/len(cpu_usage) #CPU host utilization

    #GPU Utilization
    gpu_meas=np.zeros((1,len(gpus)))
    for k in range(len(gpus)):    
        gpu_grab=urllib.urlopen(URLLIST[2+(6*m)+k]).read()
        if gpu_grab=='null':
            gpu_meas[0,k]=host_gpu_active
        else:
            gpu_read=np.array(json.loads(gpu_grab)[0]['datapoints'],dtype=np.float)[:,0]
            gpu_read=gpu_read[~np.isnan(gpu_read)]
            temp2=np.float(len(gpu_read[gpu_read>0]))
            host_gpu_active=temp2/len(gpu_read)
            gpu_meas[0,k]=host_gpu_active
    HostSummary.append([publicIP[m+1],teamname[m+1][0:teamname[m+1].find('.')], host_cpu_usage,gpu_meas[0,0],gpu_meas[0,1], gpu_meas[0,2],gpu_meas[0,3]])#,disk_space_change])    

with open('output.csv', 'wb') as fp:
    a = csv.writer(fp, delimiter=',')
    a.writerows(HostSummary) 

