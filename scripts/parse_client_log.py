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
    client_wise = {}
    with open(infile) as f:
        for line in f.readlines():
            if not "start" in line and not "end" in line:
                continue
            s = line.split()
            if s[-1] != "start" and s[-1] != "end":
                continue
            start = s[-1]=="start"
            client_id = int(s[4])
            if client_id not in client_wise:
                client_wise[client_id] = []

            ts_str = "%s %s"%(s[6], s[7])
            ts = int(datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f").timestamp()*1000)
            fn = "%s - %s"%(s[0], s[2])
            topic = s[9]

            client_wise[client_id].append((ts, fn, start, topic))

    fn_times = []

    for client_id in client_wise:
        if client_id < 200:
            continue
       
        fn_start = {} 
        for (ts, fn, start, topic) in client_wise[client_id]:
            #print (client_id, ts, fn, start, topic)

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
                fn_times.append([client_id, fn, exec_time, fn_start[fn][topic][idx]])
                del fn_start[fn][topic][idx]

    df = pd.DataFrame(fn_times, columns=["client_id", "fn", "exec_time", "start_ts"])
    #df.to_csv(join(outdir, "fn-exec_times.csv"))
    return df

def get_conf(f):
    f = f[:-4]
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
    plt.savefig(join(outdir, "fn_exec_times.png"), bbox_inches="tight")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-I", dest='indir', required=True, help="Dir containing the logs")
    parser.add_argument("-O", dest='outdir', default=".", help="Dir to store the output plot(s)")

    args = parser.parse_args()

    main(args.indir, args.outdir)
