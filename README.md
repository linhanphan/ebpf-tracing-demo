# Introduction

This repository hosts an eBPF program designed to monitor HTTP traffic on a server, tracking metrics such as request counts, response totals, success rates, and the latency (average, minimum, maximum) associated with requests per IP address.

The core strategy involves integrating a function within the eBPF socket filter to intercept both incoming and outgoing HTTP traffic, subsequently storing this data in a BPF map for further analysis by a userspace application.

To emulate server response times, we've developed a Python web application server. This server randomly generates an integer, pauses for "x" milliseconds (where 0 < x < 10), and then sends this number back to the client. Should this number be divisible by 5, the server issues an HTTP 500 error to mimic a request failure.

An alternative method for HTTP traffic capture involves embedding an eBPF program within system call functions, such as accept4, read, write, and close, regarding socket operations. The code for this approach will be submitted soon.

Below is the guideline to run the program.

# Installing BCC

Currently, BCC packages for both the Ubuntu Universe, and the iovisor builds are outdated. This is a known and tracked in:

- [Universe - Ubuntu Launchpad](https://bugs.launchpad.net/ubuntu/+source/bpfcc/+bug/1848137)
- [iovisor - BCC GitHub Issues](https://github.com/iovisor/bcc/issues/2678)
  Currently, [building from source](#ubuntu---source) is currently the only way to get up to date packaged version of bcc.

Run below commands in sudo

```bash
sudo add-apt-repository ppa:hadret/bpfcc
sudo apt update
sudo apt-get install bpfcc-tools linux-headers-$(uname -r)
```

# Installing Docker Compose

Using [docker.sh](/docker.sh) script

# Run the program

Run docker compose file to get docker bridge name

```bash
sudo docker compose up --build
```

Get bridge name of client network, for example we will monitor interface **br-2b4e89c112d8**

![](/img/bridge.png)

Run the app server

```bash
sudo apt-get -y install python3-pip
pip install flask
python3 app.py
```

Run the eBPF program (with sudo)

```bash
python3 ./http_filter.py -i br-2b4e89c112d8
```

Open another terminal to run the docker compose again to send HTTP request and you can see the result from eBPF program

![](/img/http_metric.png)

**Version 2 (monitor by port for multiple services)**
![](/img/metric_v2.png)

# Reference

The program is developed based on below eBPF examples and Internet resources:

https://github.com/iovisor/bcc

https://github.com/iovisor/bcc/tree/master/examples/networking/http_filter

https://gist.github.com/sunhay/02f235f2942403fada25063242a3aeb1
