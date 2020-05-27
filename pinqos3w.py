# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Description: QoS calculator that uses ICMP protocol 
            to calculate it using Regular Expression
            SO: Windows.
"""

import os
import time
import sys
import re
import statistics
import subprocess
import csv
import getpass
import socket
import json

__author__ = "Jean Nunes Ribeiro Araujo"
__copyright__ = "Copyright 2020, UFMG"
__credits__ = ["Pablo Rocha Moreira"]
__license__ = "GPL"
__version__ = "3.0.0"
__maintainer__ = "Jean Nunes Ribeiro Araujo"
__email__ = "jean.to@gmail.com"
__status__ = "Development"

start_time = time.time()

class bcolors:
    HEADER  = '\033[95m'
    OKBLUE  = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'

def check_args():
    if len(sys.argv) != 3:
        print(bcolors.FAIL, "Uso opcional: python pinqos3w.py [IP de destino] [Qtd. Pings]", bcolors.ENDC)
    
def calculate_QoS(bw = 10, end='108.177.13.100'):
    check_args()
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else: ip = end

    if len(sys.argv) > 2:
        pings = int(sys.argv[2])
    else: pings = 100

    ping  = "ping -n " + str(pings) + " -l 1472 " + ip + " > pings.txt"
    print
    print(bcolors.OKBLUE + "--- Realizando coleta de dados ---" + bcolors.ENDC)
    subprocess.call(ping.split(), shell=True)
    f     = open("pings.txt","r")
    f1    = f.readlines()
    trans = re.search(r'E\w+ = \d+', str(f1)).group()
    trans = int(re.search(r'\d+', trans).group())
    recv  = re.search(r'R\w+ = \d+', str(f1)).group()
    recv  = int(re.search(r'\d+', recv).group())

    stats = list()
    for m in re.finditer(r'tempo=\d+ms', str(f1)):
        tempo = float(re.search(r'\d+', m.group()).group())
        stats.append(tempo)

    print(bcolors.WARNING + '--- Calculando QoS para o host' + ip + " usando " + str(pings) + " pacotes ---" + bcolors.ENDC)

    if not len(stats):
        return
    
    jitter      = statistics.variance(stats)
    loss        = trans - recv
    delay       = statistics.mean(stats)
    throughput  = (int(bw)/(delay/1000))/1000

    total_loss  = loss
    total_loss *= float(100)
    total_loss /= pings

    sinal_wifi = sinal()
    if not sinal_wifi:
        sinal_wifi = "Não conectado!"

    print()
    print(bcolors.OKGREEN + "--- " + ip + ": Estatísticas de QoS ---" + bcolors.ENDC)
    print(str(trans) + " pacotes transmitidos. " + str(recv) + " pacotes recebidos. " + str(loss) + " pacotes perdidos.")
    print("Delay: ", delay)
    print("Jitter: ", jitter)
    print("Vazão: ", throughput)
    print("% perda de pacotes: " + str(total_loss) + "%")
    print("Nível do sinal da rede wifi: ", sinal_wifi)

    return {"jitter": str(jitter), "delay": str(delay),
            "packet_loss": str(total_loss), 
            "throughput": str(throughput), 
            "signal_level": str(sinal_wifi[:-1])}

def sinal():
    iwlist = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'])
    signal = re.search(r'\d+%', str(iwlist)).group()
    return signal

def main(mos, bw):
    report = calculate_QoS(bw)
    print
    print(bcolors.OKGREEN + "--- COPIE A LINHA ABAIXO E COLE EM http://www.dontpad.com/qos_unicatolica/ ---" + bcolors.ENDC)
    print(str(mos) + ";" + report['delay'] + ";" + report['jitter'] + ";" + report['packet_loss'] + ";" + report['throughput'] + ";" + report['signal_level'])


if __name__ == '__main__':

    print("--- MOS: Qualidade do Vídeo ---")
    print("[1] Muito ruim - muito incômodo]")
    print("[2] Ruim - incômodo]")
    print("[3] Regular - levemente incômodo]")
    print("[4] Bom - não incômodo]")
    print("[5] Excelente - falhas imperceptíveis]")
    mos = input("Informe a sua opinião sobre a qualidade [1-5]: ")
    bw  = input("Informe a sua largura de banda (Ex. 10): ")
    main(mos, bw)