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

def get_request_wise(loglist):
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
            request_wise[request].append([fn, exec_time, fn_start[fn][topic][idx], ts])
            del fn_start[fn][topic][idx]
        #print(ts, fn, start, topic, request)
    #print(" ")
    return request_wise

def parse_client_log(clientlog):
    loglist = []
    with open(clientlog) as f:
        for line in f.readlines():
            if not "start" in line and not "end" in line:
                continue
            s = line.split()
            if s[-1] != "start" and s[-1] != "end":
                continue
            if int(s[4]) < 200:
                continue
            start = s[-1]=="start"
            ts_str = "%s %s"%(s[6], s[7])
            ts = int(datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f").timestamp()*1000)
            fn = "%s - %s"%(s[0], s[2])
            topic = s[9]
            #print(topic)
            if not start:
                loglist.append((ts, fn, start, topic, s[-3]))
            else:
                loglist.append((ts, fn, start, topic, -1))
    
    request_wise = get_request_wise(loglist)
    
    return loglist, request_wise

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

    request_wise = get_request_wise(loglist)
    
    return loglist, request_wise


def main(clientlog, brokerlog, outfile):
    clientlog, client_rw = parse_client_log(clientlog)
    brokerlog, broker_rw = parse_broker_log(brokerlog)

    time_proportion = {}
    for request in client_rw:
        if request in broker_rw:
            time_proportion[request] = []
            startup = broker_rw[request][0][2] - client_rw[request][0][2]
            closing = client_rw[request][0][3] - broker_rw[request][0][3]
            time_proportion[request].append(client_rw[request][0][1])
            time_proportion[request].append(broker_rw[request][0][1])
            time_proportion[request].append(startup)
            time_proportion[request].append(closing)
    
    output = open(outfile, 'w') 
    print ("{:<15} {:<15} {:<15} {:<15} {:<15}".format('REQUEST_ID', 'C_EXEC_TIME', 'B_EXEC_TIME', 'C_TO_B', 'B_TO_C'), file=output) 

    for key, value in time_proportion.items(): 
        c_exec, b_exec, ctob, btoc = value 
        print ("{:<15} {:<15} {:<15} {:<15} {:<15}".format(key, c_exec, b_exec, ctob, btoc), file=output) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-C", dest='clientlog', required=True, help="File containing the client logs")
    parser.add_argument("-B", dest='brokerlog', required=True, help="File containing the server logs")
    parser.add_argument("-O", dest='outfile', default="proportional_output.log", help="Output file")

    args = parser.parse_args()

    main(args.clientlog, args.brokerlog, args.outfile)
