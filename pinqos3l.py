# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
Description: QoS calculator that uses ICMP protocol 
            to calculate it using SO commands
            SO: Linux.
"""

import re
import subprocess
import csv
import sys
import os

__author__ = "Jean Nunes Ribeiro Araujo"
__copyright__ = "Copyright 2020, UFMG"
__credits__ = ["Pablo Rocha Moreira"]
__license__ = "GPL"
__version__ = "3.0.0"
__maintainer__ = "Jean Nunes Ribeiro Araujo"
__email__ = "jean.to@gmail.com"
__status__ = "Development"

class bcolors:
    HEADER  = '\033[95m'
    OKBLUE  = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL    = '\033[91m'
    ENDC    = '\033[0m'

def check_args():
    if len(sys.argv) != 3:
        print(bcolors.FAIL + "Uso opcional: python pinqos3w.py [IP de destino] [Qtd. Pings]" + bcolors.ENDC)
    
def calculate_QoS(bw = 10, end='108.177.13.100'):
    check_args()
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else: ip = end

    if len(sys.argv) > 2:
        pings = int(sys.argv[2])
    else: pings = 100  

    ping_c  = "ping -c " + str(pings) + " -s 1400 " + ip + " > pings.txt"
    trans_c = "cat pings.txt | grep packets\ transmitted | awk '{print $1}'"
    recv_c  = "cat pings.txt | grep packets\ transmitted | awk '{print $4}'"
    stats_c = "cat pings.txt | grep rtt | awk '{print $4}'"

    print
    print(bcolors.OKBLUE + "--- Realizando coleta de dados ---" + bcolors.ENDC)

    try:
        os.system(ping_c)
        trans = int(subprocess.check_output(trans_c, shell=True))
        recv  = int(subprocess.check_output(recv_c, shell=True))
        stats = subprocess.getoutput(stats_c)
    except ValueError:
        return {}

    if not len(stats):
        return {}

    print(bcolors.WARNING + '--- Calculando QoS para o host ' + ip + " usando " + str(pings) + " pacotes ---" + bcolors.ENDC)
    
    jitter      = float(stats.split('/')[3])
    loss        = trans - recv
    delay       = float(stats.split('/')[1])
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
    print("Vazao: ", throughput)
    print("% perda de pacotes: " + str(total_loss) + "%")
    print("Nivel do sinal da rede wifi: ", sinal_wifi)

    return {"jitter": str(jitter), "delay": str(delay),
            "packet_loss": str(total_loss), 
            "throughput": str(throughput), 
            "signal_level": str(sinal_wifi)}

def sinal():
    signal = subprocess.check_output(['nmcli', '-t', '-f', 'ALL', 'dev', 'wifi'])
    if signal:
        signal = re.search(r'Mbit/s:\d+', str(signal)).group()
        signal = re.search(r'\d+', str(signal)).group()
    
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