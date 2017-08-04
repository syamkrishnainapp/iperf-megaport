import os
import csv
import json
import shutil
import zipfile
import platform
import subprocess as sub
from conf import *
from datetime import datetime
from time import sleep, time
from multiprocessing import Process
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict as od
from db import Base, Ignition, Internalnetworkdata

Base.metadata.bind = Ignition
Session = sessionmaker(bind=Ignition)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def saveResult(jsonFIle, file_count, file_size, iteration_number):
    # Parse variables from iperf result
    with open(jsonFIle) as iperf_results:
        data = json.load(iperf_results)
        time_taken = float(data["end"]["sum"]["seconds"])
        packet_loss = float(data["end"]["sum"]["lost_packets"])
        packet_loss_percentage = float(data["end"]["sum"]["lost_percent"])
        bandwidth_mbps = float(data["end"]["sum"]["bits_per_second"]) / 1000000
        transferred_bytes = float(data["end"]["sum"]["bytes"])

    session = Session()
    try:
        newNetData = Internalnetworkdata(
                    iteration_number=iteration_number,
                    file_size=file_size,
                    file_count=file_count,
                    transferred_bytes=transferred_bytes,
                    completion_time=time_taken,
                    packet_loss=packet_loss,
                    throughput=bandwidth_mbps
            )
        session.add(newNetData)
        session.commit()
        print "\nCompleted Iperf test"
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    return

def process_call_iperf(iperf_time, internal_net_ip, file_count, file_size, iperf_output, iterator):
    # Start iperf client in multi threaded mode
    sub.call(['iperf-3.1.3-win32\iperf3.exe', '-J', '-u', '-t', iperf_time, '-c', internal_net_ip, '-b', '0', '-P', file_count, '-F', 'dummy_file'], stdout=open(iperf_output, "w"))
    try:
        #save results to DB: args- output file, file_count, file_size
        saveResult(iperf_output, int(file_count), file_size, iterator)
    except KeyError:
        #This exception occurs if there is some error in the output. Usually happens because the iperf server restarts.
        sleep(120)
        sub.call(['iperf-3.1.3-win32\iperf3.exe', '-J', '-u', '-t', iperf_time, '-c', internal_net_ip, '-b', '0', '-P', file_count, '-F', 'dummy_file'], stdout=open(iperf_output, "w"))
        saveResult(iperf_output, int(file_count), file_size, iterator)
    return

def run_iperf_process_limited_time(max_seconds, iperf_time, internal_net_ip, file_count, file_size, iperf_output, iterator):
    #initialize process
    p = Process(target=process_call_iperf, args=(iperf_time, internal_net_ip, file_count, file_size, iperf_output, iterator))
    sleep_time = 10
    run_time = 0
    #log start time
    process_start_time = time()
    #start iperf call as new process
    p.start()

    while 1:
        #sleep for sometime
        sleep(sleep_time)
        run_time = time() - process_start_time

        #if process is not alive, we can break it
        if not p.is_alive():
            break
        #if process is still alive after max_seconds, we can kill it
        elif run_time > max_seconds:
            print 'Exceeded 20 minutes. Terminating and Skipping this iperf process.\n Continuing execution...'
            p.terminate()
            sub.call(['Taskkill', '/IM', 'iperf3.exe', '/F'])
            break
    return



if __name__ == '__main__':
    #Installing iperf on windows
    os.system('wget --no-check-certificate https://iperf.fr/download/windows/iperf-3.1.3-win32.zip')
    with zipfile.ZipFile('iperf-3.1.3-win32.zip', "r") as z:
        z.extractall()
    os.remove('iperf-3.1.3-win32.zip')

    # Internal network IP
    internal_net_ip = raw_input("\nPlease enter the IP address of the server you are trying to connect to: ")

    # ==================== GLOBAL TESTING ==================== #
    start_date = datetime.now().strftime('%Y%m%d-%H%M')
    iterator = 1
    start = time()
    for x in range(iterations):
        stop = time() - start
        if stop >= duration:
            break

        print "\n#######################################################\n"
        print "                    Iteration: " + str(iterator)
        print "\n#######################################################\n"

        iteration_start_time = datetime.now().strftime('%Y-%m-%d %H:%M')

        # ==================== IPERF ==================== #
        internal_net_csv_file = 'iperf_results.csv'
        iperf_output = 'iperf_results.json'
        #Requirement - run iperf for 1 minute and save metrics to DB
        iperf_time = '60'
        sub.call(['iperf-3.1.3-win32\iperf3.exe', '-J', '-u', '-t', iperf_time, '-c', str(internal_net_ip), '-b', '0'], stdout=open(iperf_output, "w"))
        saveResult(iperf_output, 0, 0, iterator)

        #Iterate through each configuration
        for file_info in file_config_list:
            #Create dummy file based on config
            sub.call(['fsutil', 'file', 'createnew', 'dummy_file', '%s'%(file_info[0])])
        
            #seconds since script started
            time_elapsed = start - time()
            if (duration - time_elapsed) > 86400:
                iperf_time = '86400'
            else:
                iperf_time = str(duration - time_elapsed)
            if int(file_info[1]) > 74:
                file_count = '74'
            else:
                file_count = str(file_info[1])

            print '\nThe file count for new iperf is:', file_count, '\n'
        
            run_iperf_process_limited_time(1200, iperf_time, internal_net_ip, file_count, file_info[0], iperf_output, iterator)

            #remove container folder and contents without prompt
            os.system('del dummy_file /s /q')
        
            print 'A batch finshed uploading'

        print "\nIteration %s completed\n" % iterator

        iterator += 1   #increment iterator variable
    os.system('rmdir iperf-3.1.3-win32 /s /q')
    os.remove(jsonFIle)
    print "----------------------------------------------------------------------------------"
    print " All tests are successfully completed and the results are transferred to database "
    print "----------------------------------------------------------------------------------"

