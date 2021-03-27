import sys
import time
import requests
import random
# import numpy as np
import SamplingReconstruct
ips=["172.28.2.196","172.28.2.197","172.28.2.198","172.28.2.199","172.28.2.200"]
container_name=['cpu_ut','net_i','net_o','fs_r','fs_w','cpu_co','mem_by']
pod_name=['cpu_us','mem_rs','fs_us','cpu_ut','net_i','net_o','fs_r','fs_w']
vm_name=['cpu_us','cpu_id','cpu_io','cpu_ir','cpu_ni','cpu_so',
'cpu_st','cpu_sy','cpu_ur','mem_to','mem_us','mem_bu','mem_ca',
'mem_fr','mem_sr','mem_su','disk_r','disk_w','net_o','net_i',
'intr','mem_to']
machine_num=len(ips)
vm_indicator_num=len(vm_name)
query_container=['sum(irate(container_cpu_usage_seconds_total{image!="",container_label_io_kubernetes_pod_name=""}[1m])) without (cpu)',
'sum(rate(container_network_transmit_bytes_total{image!="",container_label_io_kubernetes_pod_name=""}[1m])) without (interface)',
'sum(rate(container_network_receive_bytes_total{image!="",container_label_io_kubernetes_pod_name=""}[1m])) without (interface)',
'sum(rate(container_fs_reads_bytes_total{image!="",container_label_io_kubernetes_pod_name=""}[1m])) without (device)',
'sum(rate(container_fs_writes_bytes_total{image!="",container_label_io_kubernetes_pod_name=""}[1m])) without (device)',
'machine_cpu_cores',
'machine_memory_bytes']
query_pod=['sum by(container_label_io_kubernetes_pod_name, container_label_io_kubernetes_namespace) (rate(container_cpu_usage_seconds_total{image!="",container_label_io_kubernetes_pod_name!=""}[1m]))',
'sum by(container_label_io_kubernetes_pod_name, container_label_io_kubernetes_namespace) (container_memory_rss{image!="",container_label_io_kubernetes_pod_name!=""})',
'sum by(container_label_io_kubernetes_pod_name, container_label_io_kubernetes_namespace) (container_fs_usage_bytes{image!="",container_label_io_kubernetes_pod_name!=""})',
'sum(irate(container_cpu_usage_seconds_total{image!="",container_label_io_kubernetes_pod_name!=""}[1m])) without (cpu)',
'sum(rate(container_network_transmit_bytes_total{image!="",container_label_io_kubernetes_pod_name!=""}[1m])) without (interface)',
'sum(rate(container_network_receive_bytes_total{image!="",container_label_io_kubernetes_pod_name!=""}[1m])) without (interface)',
'sum(rate(container_fs_reads_bytes_total{image!="",container_label_io_kubernetes_pod_name!=""}[1m])) without (device)',
'sum(rate(container_fs_writes_bytes_total{image!="",container_label_io_kubernetes_pod_name!=""}[1m])) without (device)']
query_vm=['1-(sum(rate(node_cpu_seconds_total{cpu!="",mode="idle"}[1m])) without (cpu))',
'sum(rate(node_cpu_seconds_total{cpu!="",mode="idle"}[1m])) without (cpu)',
'sum(rate(node_cpu_seconds_total{cpu!="",mode="iowait"}[1m])) without (cpu)',
'sum(rate(node_cpu_seconds_total{cpu!="",mode="irq"}[1m])) without (cpu)',
'sum(rate(node_cpu_seconds_total{cpu!="",mode="nice"}[1m])) without (cpu)',
'sum(rate(node_cpu_seconds_total{cpu!="",mode="softirq"}[1m])) without (cpu)',
'sum(rate(node_cpu_seconds_total{cpu!="",mode="steal"}[1m])) without (cpu)',
'sum(rate(node_cpu_seconds_total{cpu!="",mode="system"}[1m])) without (cpu)',
'sum(rate(node_cpu_seconds_total{cpu!="",mode="user"}[1m])) without (cpu)',
'node_memory_MemTotal_bytes',
'1-(node_memory_MemFree_bytes/ node_memory_MemTotal_bytes)',
'node_memory_Buffers_bytes/ node_memory_MemTotal_bytes',
'node_memory_Cached_bytes/ node_memory_MemTotal_bytes',
'node_memory_MemFree_bytes/ node_memory_MemTotal_bytes',
'node_memory_SReclaimable_bytes/ node_memory_MemTotal_bytes',
'node_memory_SUnreclaim_bytes/ node_memory_MemTotal_bytes',
'sum(node_disk_read_bytes_total) without (device)',
'sum(node_disk_written_bytes_total) without (device)',
'sum(irate(node_network_transmit_bytes_total[1m])) without (device)',
'sum(irate(node_network_receive_bytes_total[1m])) without (device)',
'avg_over_time(node_intr_total[1m])',
'sum(rate(container_memory_usage_bytes{image!=""}[1m]))']

# 返回prometheus相关数据的json文件
def collect_promql(ip,opt):
    url_ip = "http://" + ip + ":9090/api/v1/query?query="
    url = url_ip + opt
    try:
        results = requests.get(url)
        r = results.json()
        return r
    except Exception as e:
        print(e)
        return None

# 采集prometheuss上查询的container,vm,pod,采集k8s中的Pod任务信息，采集PDU中的能耗数据
def collect_vm_pod_container(choice):
    vm_indicator=[]
    pod_indicator=[]
    container_indicator=[]
    i=-1
    for ip in ips:
        i+=1
        if choice[i]==0:
            continue
        for query in query_vm:
            r = collect_promql(ip, query)
            if r:
                for data in r['data']['result']:
                    vm_indicator.append(data)
        for query in query_container:
            r = collect_promql(ip, query)
            if r:
                for data in r['data']['result']:
                    container_indicator.append(data)
        for query in query_pod:
            r = collect_promql(ip, query)
            if r:
                for data in r['data']['result']:
                    pod_indicator.append(data)
    return vm_indicator.copy()

# 根据choice采集目的
def collect_by(choice):
    start_time=time.time()
    collect_vm_pod_container(choice)
    end_time=time.time()
    print('prometheus cost',end_time-start_time)
    # collect_k8s()
    # k8s_time=time.time()
    # collect_container()
    # container_time=time.time()
    # collect_Pod()
    # pod_time=time.time()
# ips path,querycode path,indicater name,sampling_rate
if __name__ == '__main__':
    sampling_rate=1
    sr1 = SamplingReconstruct.SamplingReconstruct(machine_num, sampling_rate, vm_indicator_num)
    choice = sr1.sampling()
    vm_arr=collect_by(choice)
    temp_arr = sr1.reconstruct(vm_arr, choice)
    print(choice,temp_arr)