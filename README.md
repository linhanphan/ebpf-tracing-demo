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

# Reference

The program is developed based on below eBPF examples and Internet resources:

https://github.com/iovisor/bcc

https://github.com/iovisor/bcc/tree/master/examples/networking/http_filter

https://gist.github.com/sunhay/02f235f2942403fada25063242a3aeb1
