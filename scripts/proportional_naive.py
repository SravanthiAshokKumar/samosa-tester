import argparse
from os import listdir
from os.path import join, isfile
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
from matplotlib import font_manager
import seaborn as sns

def parse_client_log(clientlog):
    loglist = []
    with open(clientlog) as f:
        for line in f.readlines():
            if not "start" in line and not "end" in line:
                continue
            s = line.split()
            if s[-1] != "start" and s[-1] != "end":
                continue
            start = s[-1]=="start"
            ts_str = "%s %s"%(s[6], s[7])
            ts = int(datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f").timestamp()*1000)
            fn = "%s - %s"%(s[0], s[2])
            topic = s[8]
            if not start:
                loglist.append((ts, fn, start, topic, s[-3]))
            else:
                loglist.append((ts, fn, start, topic, -1))
    
    request_wise = {}
    fn_start = {} 
    for (ts, fn, start, topic, request) in loglist:
        if fn not in fn_start:
            fn_start[fn] = {}

        if topic not in fn_start[fn]:
            fn_start[fn][topic] = {}

        if start:
            idx = len(fn_start[fn][topic])
            fn_start[fn][topic][idx] = ts
        else:
            idx = len(fn_start[fn][topic])-1
            assert (idx in fn_start[fn][topic])
            exec_time = ts - fn_start[fn][topic][idx]
            request_wise[request] = []
            request_wise[request].append([fn, exec_time, fn_start[fn][topic][idx]])
            del fn_start[fn][topic][idx]
    
    return request_wise

def parse_broker_log(brokerlog):
    loglist = []
    with open(brokerlog) as f:
        for line in f.readlines():
            if not "start" in line and not "end" in line:
                continue
            s = line.split()
            if s[4] != "start" and s[4] != "end":
                continue
            start = s[4]=="start"
            ts_str = "%s %s"%(s[6], s[7])
            ts = int(datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f").timestamp()*1000)
            fn = "%s - %s"%(s[0], s[2])
            topic = s[9]
            request = s[-1]

            loglist.append((ts, fn, start, topic, request))
        
    request_wise = {}
    fn_start = {} 
    for (ts, fn, start, topic, request) in loglist:
        if fn not in fn_start:
            fn_start[fn] = {}

        if topic not in fn_start[fn]:
            fn_start[fn][topic] = {}

        if start:
            idx = len(fn_start[fn][topic])
            fn_start[fn][topic][idx] = ts
        else:
            idx = len(fn_start[fn][topic])-1
            assert (idx in fn_start[fn][topic])
            exec_time = ts - fn_start[fn][topic][idx]
            request_wise[request] = []
            request_wise[request].append([fn, exec_time, fn_start[fn][topic][idx]])
            del fn_start[fn][topic][idx]

    return request_wise


def main(clientlog, brokerlog):
    clientlog = parse_client_log(clientlog)
    brokerlog = parse_broker_log(brokerlog)
    time_proportion = {}
    for request in clientlog:
        if request in brokerlog:
            time_proportion[request] = []
            time_proportion[request].append(clientlog[request][0][1])
       	    time_proportion[request].append(brokerlog[request][0][1])
    print(time_proportion)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-C", dest='clientlog', required=True, help="File containing the client logs")
    parser.add_argument("-B", dest='brokerlog', default=".", help="File containing the server logs")

    args = parser.parse_args()

    main(args.clientlog, args.brokerlog)
