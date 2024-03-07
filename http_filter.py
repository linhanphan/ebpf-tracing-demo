from __future__ import print_function
from bcc import BPF
from ctypes import *
from struct import *
from sys import argv
from socket import inet_ntop, AF_INET
from datetime import datetime

import socket
import os
import struct
import time
import fcntl

host_ip = "127.0.0.1"

# copy the data from bpf map to a python dictionary
raw_data = {}
"""
raw_data = {
  timestamp: { 
    scr_ip: "ip_address",
    dst_ip: "ip_address",
    scr_port: "port",
    dst_port: "port",
    length: "length",
    payload: "payload"
  }
}
"""

# define a dictionary to store the processed data
"""
processed_data = {
    "ip_address": {
        "ingress": { "ip_address:port": [timestamp, timestamp, ...] }, 
        "egress": { "ip_address:port": [timestamp, timestamp, ...] },
        "complete: [(timestamp, timestamp), (timestamp, timestamp),...],
        "success": [(timestamp, timestamp), (timestamp, timestamp),...],
        "success_delay": [time_ms, time_ms, ...],
        "fail": [(timestamp, timestamp), (timestamp, timestamp),...],
        "fail_delay": [time_ms, time_ms, ...]
}

Calculate the metrics for the processed data
response_rate = egress / ingress
success_rate = success / ingress
average_response_time = sum(success_delay) / len(success_delay)
average_fail_time = sum(fail_delay) / len(fail_delay)
"""
p_data = {}


def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # The ioctl call will get the IP address assigned to the interface
        return socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack("256s", bytes(ifname[:15], "utf-8")),
            )[20:24]
        )
    except IOError:  # Handle error if the interface does not exist or is down
        return "Interface not found or down"


def get_first_line(s):
    return s.split(b"\r\n")[0].decode()


# print function
def printStats():
    for k, v in sorted(http_events.items(), key=lambda ts: ts[0].value):

        # copy the data from bpf map to a raw_data dictionary
        raw_data[k.value] = v

        src_ip = inet_ntop(AF_INET, pack(">I", v.src_ip))
        dst_ip = inet_ntop(AF_INET, pack(">I", v.dst_ip))
        src_port = str(v.src_port)
        dst_port = str(v.dst_port)
        # ts = k.value
        # check if this is egress packet
        if src_ip == host_ip:
            # first egress packet
            if dst_ip not in p_data:
                p_data[dst_ip] = {
                    "ingress": {},
                    "egress": {dst_ip + ":" + dst_port: [k.value]},
                    "complete": [],
                    "success": [],
                    "success_delay": [],
                    "fail": [],
                    "fail_delay": [],
                }
            else:
                # if we already had data of ingress packet
                if dst_ip + ":" + dst_port not in p_data[dst_ip]["egress"]:
                    p_data[dst_ip]["egress"][dst_ip + ":" + dst_port] = [k.value]
                else:
                    p_data[dst_ip]["egress"][dst_ip + ":" + dst_port].append(k.value)

                if dst_ip + ":" + dst_port in p_data[dst_ip]["ingress"]:
                    pair_req = (
                        p_data[dst_ip]["ingress"][dst_ip + ":" + dst_port],
                        k.value,
                    )
                    p_data[dst_ip]["complete"].append(pair_req)
                    delay_ms = (
                        k.value - p_data[dst_ip]["ingress"][dst_ip + ":" + dst_port][-1]
                    ) / 1000000

                    status = get_first_line(v.payload).split(" ")[1]
                    if status == "200":
                        p_data[dst_ip]["success"].append(pair_req)
                        p_data[dst_ip]["success_delay"].append(delay_ms)
                    else:
                        # assum that only traffic with status 200 is success
                        p_data[dst_ip]["fail"].append(pair_req)
                        p_data[dst_ip]["fail_delay"].append(delay_ms)
        else:
            # if this is the first ingress packet
            if src_ip not in p_data:
                p_data[src_ip] = {
                    "ingress": {src_ip + ":" + src_port: [k.value]},
                    "egress": {},
                    "complete": [],
                    "success": [],
                    "success_delay": [],
                    "fail": [],
                    "fail_delay": [],
                }
            else:
                if src_ip + ":" + src_port not in p_data[src_ip]["ingress"]:
                    p_data[src_ip]["ingress"][src_ip + ":" + src_port] = [k.value]
                else:
                    p_data[src_ip]["ingress"][src_ip + ":" + src_port].append(k.value)
                # since we iterate in order, we can assume that the first packet is the request
                # and the second packet is the response so skip checking for the request

        # print(p_data)
    # clear the bpf map
    try:
        http_events.clear()
    except:
        print("cleanup exception.")

    os.system("clear")
    # print the processed data
    # print("Processed Data")
    # print(p_data)
    print("---------- %s ----------" % (str(datetime.now())))
    print("---------- Total logs: %d ----------" % len(raw_data))
    print(
        "%-15s %-15s %-15s %-20s %-25s %-25s"
        % (
            "IP",
            "Total Requests",
            "Response Rate",
            "Total success (Rate)",
            "Avg/Max/Min Success Time",
            "Avg/Max/Min Fail Time",
        )
    )

    for ip, data in p_data.items():
        # calculate the metrics
        response_rate = len(data["egress"]) * 100 / len(data["ingress"])
        success_rate = len(data["success"]) * 100 / len(data["ingress"])
        if len(data["success_delay"]) == 0:
            average_success_time = 0
        else:
            average_success_time = sum(data["success_delay"]) / len(
                data["success_delay"]
            )
        if len(data["fail_delay"]) == 0:
            average_fail_time = 0
        else:
            average_fail_time = sum(data["fail_delay"]) / len(data["fail_delay"])
        print(
            "%-15s %-15d %-15.2f %d (%.2f) \t\t %.2f/%d/%-15d \t %.2f/%d/%-15d"
            % (
                ip,
                len(data["ingress"]),
                response_rate,
                len(data["success"]),
                success_rate,
                average_success_time,
                max(data["success_delay"], default=0),
                min(data["success_delay"], default=0),
                average_fail_time,
                max(data["fail_delay"], default=0),
                min(data["fail_delay"], default=0),
            )
        )


# args
def usage():
    print("USAGE: %s [-i <if_name>]" % argv[0])
    print("")
    print("Try '%s -h' for more options." % argv[0])
    exit()


# help
def help():
    print("USAGE: %s [-i <if_name>]" % argv[0])
    print("")
    print("optional arguments:")
    print("   -h                       print this help")
    print("   -i if_name               select interface if_name. Default is enp0s3")
    print("")
    print("examples:")
    print("    http_monitor              # bind socket to enp0s3")
    print("    http_monitor -i wlan0     # bind socket to wlan0")
    exit()


# arguments
interface = "enp0s3"

if len(argv) == 2:
    if str(argv[1]) == "-h":
        help()
    else:
        usage()

if len(argv) == 3:
    if str(argv[1]) == "-i":
        interface = argv[2]
    else:
        usage()

if len(argv) > 3:
    usage()

print("binding socket to '%s'" % interface)

host_ip = get_ip_address(interface)

# initialize BPF - load source code from http-parse-complete.c
bpf = BPF(src_file="http_filter_ebpf.c", debug=0)

# load eBPF program tcp_monitor of type SOCKET_FILTER into the kernel eBPF vm
# more info about eBPF program types
# http://man7.org/linux/man-pages/man2/bpf.2.html
function_monitor_filter = bpf.load_func("http_filter", BPF.SOCKET_FILTER)

# create raw socket, bind it to interface
# attach bpf program to socket created
BPF.attach_raw_socket(function_monitor_filter, interface)

# get pointer to bpf map of type hash
http_events = bpf.get_table("http_events")

while 1:
    printStats()
    time.sleep(1)
