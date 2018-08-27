#!/usr/bin/env python3
# _*_coding:UTF-8_*_

import numpy as np
import matplotlib.pyplot as plt
import socket, sys, os


def main():
    if len(sys.argv) < 2:
        print("Lack of the file name which to read from!")
        pwd = os.getcwd()
        tpsname = pwd + '/log/tpsrecord.txt'
        print('Use the default tpsname:\n', tpsname)
    else:
        tpsname = sys.argv[1]

    xlabel = "Transaction per second(tps)"
    ylabel = "Test result number"
    figname = "tpsresult"

    datamatri = []
    f = open(tpsname, "r")
    for line in f.readlines():
        lineArr = line.strip().split()
        datamatri.append(float(lineArr[0]))
    f.close()
    #datamatri = np.random.randn(75)
    plt.hist(datamatri, histtype='bar')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(figname, dpi=600)
    plt.show()

if __name__ == '__main__':
    main()
