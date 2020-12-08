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

def parse_log(infile):
    loglist = []
    with open(infile) as f:
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
            #topic = s[-3]

            loglist.append((ts, fn, start))

    fn_times = []
    fn_start = {} 
    for (ts, fn, start) in loglist:
        #print (client_id, ts, fn, start, topic)

        if fn not in fn_start:
            fn_start[fn] = {}

        # if topic not in fn_start[fn]:
        #     fn_start[fn][topic] = {}

        if start:
            idx = len(fn_start[fn])
            fn_start[fn][idx] = ts
        else:
            idx = len(fn_start[fn])-1
            assert (idx in fn_start[fn])
            exec_time = ts - fn_start[fn][idx]
            fn_times.append([fn, exec_time, fn_start[fn][idx]])
            del fn_start[fn][idx]

    df = pd.DataFrame(fn_times, columns=["fn", "exec_time", "start_ts"])
    #df.to_csv(join(outdir, "fn-exec_times.csv"))
    return df

def get_conf(f):
    f = f[:-4]
#    print(f)
    s = f.split("_")
    conf = {}
    for idx in range(len(s)):
        if s[idx] == "B":
            conf[s[idx]] = float(s[idx+1])
        if s[idx] == "C":
            conf[s[idx]] = int(s[idx+1])
        if s[idx] == "I":
            conf[s[idx]] = int(s[idx+1])
    return conf

def main(indir, outdir):
    files = [x for x in listdir(indir) if isfile(join(indir, x)) and x.endswith(".log")]
    aggr_df = pd.DataFrame()
    for f in files:
        df = parse_log(join(indir, f))
        conf = get_conf(f)
        for k in conf:
            df[k] = conf[k]

        aggr_df = aggr_df.append(df, ignore_index=True)
    plt.close()
    sns.catplot(data = aggr_df, col="fn", y="exec_time", hue="B", x="C", kind="box", row="I")
    #plt.xlabel("Function name")
    plt.ylabel("Execution time (ms)")
    plt.savefig(join(outdir, "fn_exec_times_server.png"), bbox_inches="tight")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-I", dest='indir', required=True, help="Dir containing the logs")
    parser.add_argument("-O", dest='outdir', default=".", help="Dir to store the output plot(s)")

    args = parser.parse_args()

    main(args.indir, args.outdir)
