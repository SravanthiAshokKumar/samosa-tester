import re
import argparse

SAMOSA_TESTER = "/home/surveillance/samosa-tester"

def grep_server(path):
    numClients = ['10', '50']
    for k in range(5):
        for i in numClients:
            sysout_orig = "pulsar-broker-surveillance-faas.out.{}".format(k+1)
            sysout = "sysout_server_B_0.01_C_{}_I_{}.log".format(i, k)

            txt1 = "PulsarDecoder - channelRead_"
            txt2 = "TopicLookupBase - lookupTopicAsync"
            f_orig = open('{}/{}'.format(path, sysout_orig), 'r')
            f = open('{}/{}'.format(path, sysout), 'w')
            for line in f_orig:
                if re.search(txt1, line) or re.search(txt2, line):
                    f.write(line)

def grep_client(path):
    numClients = ['10', '50']
    for k in range(5):
        for i in numClients:
            sysout_orig = "sysout_B_0.01_C_{}_I_{}_orig.log".format(i, k)
            sysout = "sysout_B_0.01_C_{}_I_{}.log".format(i, k)

            txt1 = "lookup - getBroker"
            txt2 = "BinaryLookupService - getPartitionedTopicMetadata"
            f_orig = open('{}/{}'.format(path, sysout_orig), 'r')
            f = open('{}/{}'.format(path, sysout), 'w')
            for line in f_orig:
                if re.search(txt1, line) or re.search(txt2, line):
                    f.write(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-M", dest='mode', required=True, help="parse client or server files")
    parser.add_argument("-I", dest='indir', help="path of the log files")

    args = parser.parse_args()

    if args.mode == 'C':
        grep_client(args.indir)
    if args.mode == 'B':
        grep_server(args.indir)
