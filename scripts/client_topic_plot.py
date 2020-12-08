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
import itertools

def get_request_wise(loglist):
    request_wise = {}
    fn_start = {} 
    for (ts, fn, start, topic, request, client_id) in loglist:
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
            request_wise[request].append([fn, exec_time, fn_start[fn][topic][idx], ts, client_id])
            del fn_start[fn][topic][idx]
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
            client_id = s[4]
            if not start:
                loglist.append((ts, fn, start, topic, s[-3], client_id))
            else:
                loglist.append((ts, fn, start, topic, -1, client_id))
    
    request_wise = get_request_wise(loglist)
    
    return loglist, request_wise


def main(clientlog, outfile):
    clientlog, client_rw = parse_client_log(clientlog)

    # figure 1
    plt.figure(0)
    plt.xlabel('request_id')
    plt.ylabel('absolute time')
    plt.xticks(rotation='vertical')
    x_elements = list(client_rw.keys())

    y1_elements = [item[0][-2] for item in list(client_rw.values())]
    plt.plot(x_elements, y1_elements, label = 'end time') 
    
    y2_elements = [item[0][-3] for item in list(client_rw.values())]
    plt.plot(x_elements, y2_elements, label = 'start time')

    plt.legend() 
    plt.savefig(outfile+"_startEndVsReqId.png")

    zoom_y1 = []
    zoom_y2 = []
    zoom_x = []
    for i in range(len(y1_elements)):
        diff = y1_elements[i] - 1607156900000
        if diff > 15000 and diff <= 35000:
            zoom_y1.append(y1_elements[i])
            zoom_y2.append(y2_elements[i])
            zoom_x.append(x_elements[i])
    
    # figure 2
    plt.figure(1)
    plt.xlabel('request_id')
    plt.ylabel('absolute time')
    plt.xticks(rotation='vertical')
    plt.plot(zoom_x, zoom_y1, label = 'end time')
    plt.plot(zoom_x, zoom_y2, label = 'start time')
    print(zoom_y1)
    print("")
    print(zoom_y2)
    plt.legend() 
    plt.savefig(outfile+"_startEndVsReqId_zoom.png")

    # figure 3
    # plt.figure(1)
    # plt.xlabel('client_id')
    # plt.ylabel('absolute time')
    # plt.xticks(rotation='vertical')
    # x_elements = [item[0][-1] for item in list(client_rw.values())]
    
    # y_elements = [item[0][-2] for item in list(client_rw.values())]
    # plt.plot(x_elements[:20], y_elements[:20], label = 'end time')
    # print(list(client_rw.values())[:20])
    # y_elements = [item[0][-3] for item in list(client_rw.values())]
    # plt.plot(x_elements, y_elements, label = 'start time')

    # plt.legend() 
    # plt.savefig(outfile+"_startEndVsClientId.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-C", dest='clientlog', required=True, help="File containing the client logs")
    parser.add_argument("-O", dest='outfile', default="client_plot", help="Output file")

    args = parser.parse_args()

    main(args.clientlog, args.outfile)
