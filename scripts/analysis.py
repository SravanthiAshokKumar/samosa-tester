import yaml
import subprocess

def modify_yaml(numClients, blockSize):
    with open('config.yaml') as f:
        doc = yaml.load(f)

    doc['numClients'] = numClients
    doc['indexConfig']['blockSize'] = blockSize

    with open('config.yaml', 'w') as f:
        yaml.dump(doc, f)


def main():
    numClients = [10, 50]
    blockSize = [0.01, 0.1, 0.5, 1]
    for k in range(5):
        for i in numClients:
            for j in blockSize:
                sysout = "sysout_B_{}_C_{}_I_{}.log".format(j, i, k)
                print(sysout)
                f = open('/home/surveillance/samosa-tester/bin/analysis/'+sysout, 'w')
                modify_yaml(i, j)
                subprocess.call(['bash', 'run.sh', 'config.yaml'], stdout=f)

if __name__ == "__main__":
    main()