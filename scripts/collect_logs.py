import yaml
import subprocess
import os
import time
import re

PULSAR_BIN = "/home/surveillance/pulsar/bin"
SAMOSA_TESTER = "/home/surveillance/samosa-tester"

def modify_yaml(numClients, blockSize):
    with open('config.yaml') as f:
        doc = yaml.load(f)

    doc['numClients'] = numClients
    doc['indexConfig']['blockSize'] = blockSize

    with open('config.yaml', 'w') as f:
        yaml.dump(doc, f)


def main():
    numClients = [10, 50]
    blockSize = [0.01]
    for k in range(5):
        for i in numClients:
            for j in blockSize:
                sysout = "sysout_B_{}_C_{}_I_{}.log".format(j, i, k)
                print(sysout)
                #os.chdir(PULSAR_BIN)
                f = open('{}/bin/analysis/client/{}'.format(SAMOSA_TESTER, sysout), 'w')
                #temp = open('{}/bin/analysis/server/temp.log'.format(SAMOSA_TESTER), 'w+')
                
                #process = subprocess.Popen('sudo ./pulsar standalone &', shell = True, stdout=temp)
                #time.sleep(20)
                #os.chdir('{}/bin'.format(SAMOSA_TESTER))
                modify_yaml(i, j)
                subprocess.call(['bash', 'run.sh', 'config.yaml'], stdout=f)
                #os.kill(process.pid+1, 9)

                # txt1 = "PulsarDecoder - channelRead_"
                # txt2 = "TopicLookupBase - lookupTopicAsync"
                # f_server = open('{}/bin/analysis/server/{}'.format(SAMOSA_TESTER, sysout_server), 'w')
                # for line in temp:
                #     if re.search(txt1, line) or re.search(txt2, line):
                #         f_server.write(line)


if __name__ == "__main__":
    main()