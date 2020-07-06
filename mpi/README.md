
# Setup

From the [Raspberry PI magazine](https://magpi.raspberrypi.org/), The MagPi, issue 87:

https://magpi.raspberrypi.org/articles/build-a-raspberry-pi-cluster-computer
https://github.com/mrpjevans/cluster-prime/

On each node, run the following:

```bash
sudo apt install mpich python3-mpi4py -y
```

Test if MPI is working on each node with:

```bash
mpiexec -n 1 hostname
```

This command should print the hostname of the node it is run on.

On the master node, run

```bash
mpiexec -n 4 --host 192.168.127.101,192.168.127.102,192.168.127.103,192.168.127.104 hostname
```

This should print the hostnames of the nodes in the list of IPs.

```bash
mpiexec -n 1 python3 prime.py 10000
```

This will execute the script locally on the node with only 1 process. Since the Raspberry Pi 4 actually has 4 cores, we can increase this to 4 to execute it even faster:

```bash
mpiexec -n 4 python3 prime.py 10000
```

But of course, we have access to a cluster so we can distribute this work on all nodes. First we need to share the script with the nodes so that it is accessible locally. I have put the script in `~/mpi/prime.py` on the master node, so we need to put it in the same directory on the worker nodes. Since this `mpi` directory might not exists, we first need to create it before copying over the python file:

```bash
ssh 192.168.127.102 'mkdir ~/mpi'
scp ~/mpi/prime.py 192.168.127.102:~/mpi/prime.py

ssh 192.168.127.103 'mkdir ~/mpi'
scp ~/mpi/prime.py 192.168.127.103:~/mpi/prime.py

ssh 192.168.127.104 'mkdir ~/mpi'
scp ~/mpi/prime.py 192.168.127.104:~/mpi/prime.py
```

Since I am running Kubernetes and some other applications on the cluster, I need to specify the correct network interface. Through `ifconfig` I found this to be the default `eth0`. We can now execute it on all nodes with

```bash
mpiexec -n 1 -mca btl_tcp_if_include eth0 --host 192.168.127.101,192.168.127.102,192.168.127.103,192.168.127.104 python3 ~/mpi/prime.py 10000
```

We can make this a bit easier by creating a file called e.g. `hosts` and populate it with the hostnames of our nodes:

```bash
# Raspberry PI cluster MPI hosts file
192.168.127.101 # rpic-master
192.168.127.102 # rpic-worker-01
192.168.127.103 # rpic-worker-02
192.168.127.104 # rpic-worker-03
```

We can test it by running

```bash
mpiexec -np 4 -mca btl_tcp_if_include eth0 --hostfile ~/mpi/hosts python3 ~/mpi/hello_world.py
```

We get the output:

```
Hello world from process  1 on node rpic-master
Hello world from process  2 on node rpic-master
Hello world from process  0 on node rpic-master
Hello world from process  3 on node rpic-master
```

But this will only print our messages from one node! What is the problem? Well, since this single node has access to 4 cores, it will in fact be able to run all processes. If we increase the number of processes to, say 12, we get

```
Hello world from process  0 on node rpic-master
Hello world from process  6 on node rpic-worker-01
Hello world from process  8 on node rpic-worker-02
Hello world from process  7 on node rpic-worker-01
Hello world from process  4 on node rpic-worker-01
Hello world from process 10 on node rpic-worker-02
Hello world from process 11 on node rpic-worker-02
Hello world from process  9 on node rpic-worker-02
Hello world from process  3 on node rpic-master
Hello world from process  5 on node rpic-worker-01
Hello world from process  1 on node rpic-master
Hello world from process  2 on node rpic-master
```

We can also specify how many `slots` each node should use:

```bash
# Raspberry PI cluster MPI hosts file
192.168.127.101 slots=1 max_slots=4 # rpic-master
192.168.127.102 slots=2 max_slots=4 # rpic-worker-01
192.168.127.103 slots=3 max_slots=4 # rpic-worker-02
192.168.127.104 slots=4 max_slots=4 # rpic-worker-03
```

The `slots` specify how many slots we want to use on the machine. The `max_slots` specify the absolute maximum, disallowing us to over-subscribe it. Running the command with 4 process now, we instead get

```
Hello world from process  3 on node rpic-worker-02
Hello world from process  2 on node rpic-worker-01
Hello world from process  1 on node rpic-worker-01
Hello world from process  0 on node rpic-master
```

I.e. the master can handle 1 process, worker 1 can handle 2, and worker 3 can handle 3. Of course, we should specify the `slots` in the hosts file in a way that reflects how we want to distribute the computational resources in the cluster. For example, it some nodes are running other services which may not allow them to use 4 cores at all times. Read more about this over at https://www.open-mpi.org/faq/?category=running#mpirun-hostfile.

So how much faster can we find primes using the cluster then? Let's first benchmark using only a single process for the primes in the first 30000 numbers:

```bash
mpiexec -np 1 -mca btl_tcp_if_include eth0 -hostfile ./hosts python3 ./prime.py 30000
```

```
Find all primes up to: 30000
Nodes: 1
Time elasped: 14.14 seconds
Primes discovered: 3245
```

Using only a single process it took 14.14 seconds. Now, let's use the full power of each quad-core in the cluster of 4 Raspberrys!

```bash
mpiexec -np 16 -mca btl_tcp_if_include eth0 -hostfile ./hosts python3 ./prime.py 30000
```

```
Find all primes up to: 30000
Nodes: 16
Time elasped: 1.58 seconds
Primes discovered: 3245
```

Now it only takes 1.58 seconds! That is 14.14/1.58 ~8.95 times faster!

## Notes

I had a problem running MPI on more than one node in the beginning, getting the error

```
--------------------------------------------------------------------------
WARNING: Open MPI failed to TCP connect to a peer MPI process.  This
should not happen.

Your Open MPI job may now fail.

Local host: rpic-worker-01
PID:        5958
Message:    connect() to 169.254.30.183:1024 failed
Error:      Operation now in progress (115)
--------------------------------------------------------------------------
```

This was probably due to the fact that I am running kubernetes and some other applications on the cluster which introduces a number of network interfaces which confuses MPI. This is solved by specifically telling MPI which interface to use for communication. By running `ifconfig` I could see that it was the defaul `eth0` interface I was supposed to use, which then can be specified as `-mca btl_tcp_if_include eth0` when running `mpiexec`.