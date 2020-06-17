# Hadoop File System (HDFS)
https://dev.to/awwsmm/building-a-raspberry-pi-hadoop-spark-cluster-8b2

## Java

Hadoop requires Java. This is installed by default for some Raspbain distributions. You can check if it is installed with the command

    java --version

If it is not installed, it has to be installed on all nodes with

    sudo apt install default-jre

or on all nodes with

    rpic-cmd "sudo apt install default-jre -y"

## Hadoop

Get the hadoop binaries from here:

    wget -c http://apache.mirrors.spacedump.net/hadoop/common/hadoop-3.2.1/hadoop-3.2.1.tar.gz

Then untar it to the `opt` directory with 

    sudo tar -xvf hadoop-3.2.1.tar.gz -C /opt/

I actually had a problem with downloading them directly to the raspberry with the tar file getting corrupt, leading to errors like `tar: Skipping to next header`. In the end I just downloaded the file to my local machine and copied it over to the raspberry using `scp`. Then it worked fine!

Rename the directory with

    cd /opt
    sudo mv hadoop-3.2.1/ hadoop

Change permission on the directory:

    sudo chown pi:pi -R /opt/hadoop
-
Add the directory to `$PATH` by editing `~/.bashrc` and adding the following commands. Note however, that on some systems, like Ubuntu 18.04 in my case, it is important where we place these lines in the file if we want to be able to execute hadoop commands remotely through SSH. One if the lines in `bashrc` might look like this:

    # If not running interactively, don't do anything
    case $- in
        *i*) ;;
        *) return;;
    esac

This means that any command which is placed after those lines won't get executed if we issue the command non-interactively, like through ssh. In other words, place the following commands above these lines. Here is a thread with the same issue: https://stackoverflow.com/questions/820517/bashrc-at-ssh-login. 

    export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")
    export HADOOP_HOME=/opt/hadoop
    export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

Edit `opt/hadoop/etc/hadoop/hadoop-env.sh` and add

    export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")

Verify installation with

    cd && hadoop version | grep Hadoop

## Spark

Download spark from https://spark.apache.org/downloads.html:

    wget -c http://apache.mirrors.spacedump.net/spark/spark-2.4.6/spark-2.4.6-bin-hadoop2.7.tgz

Move to opt as before:

    sudo tar -xvf spark-2.4.6-bin-hadoop2.7.tgz -C /opt/
    cd /opt
    sudo mv spark-2.4.6-bin-hadoop2.7/ spark
    sudo chown pi:pi -R /opt/spark

Edit `.bashrc`:

    export SPARK_HOME=/opt/spark
    export PATH=$PATH:$SPARK_HOME/bin
    
Apply with `source ~/.bashrc` and verify installation with

    cd && spark-shell --version

## HDFS

`/opt/hadoop/etc/hadoop/core-site.xml`: Make sure the ip address is using the correct alias or ip:

    <configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://rpic-master:9000</value>
    </property>
    </configuration>

`/opt/hadoop/etc/hadoop/hdfs-site.xml`:

    <configuration>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///opt/hadoop_tmp/hdfs/datanode</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///opt/hadoop_tmp/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    </configuration>

These changes will configure where the DataNode and NameNode information is stored. The replication number is here only 1 for the time being.

    sudo mkdir -p /opt/hadoop_tmp/hdfs/datanode
    sudo mkdir -p /opt/hadoop_tmp/hdfs/namenode
    sudo chown pi:pi -R /opt/hadoop_tmp

`/opt/hadoop/etc/hadoop/mapred-site.xml`:

    <configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    </configuration>

`/opt/hadoop/etc/hadoop/yarn-site.xml`:

    <configuration>
        <property>
            <name>yarn.nodemanager.aux-services</name>
            <value>mapreduce_shuffle</value>
        </property>
        <property>
            <name>yarn.nodemanager.auxservices.mapreduce.shuffle.class</name>  
            <value>org.apache.hadoop.mapred.ShuffleHandler</value>
        </property>
    </configuration>

Now we format the HDFS:

    hdfs namenode -format -force

Boot the HDFS

    start-dfs.sh
    start-yarn.sh
    
Test with

    hadoop fs -mkdir /tmp
    hadoop fs -ls /

(If something goes wrong and you need to reset, you can stop with `stop-all.sh`)

We might get two errors with this setup however. The first is

    OpenJDK Server VM warning: You have loaded library /opt/hadoop/lib/native/libhadoop.so.1.0.0 which might have disabled stack guard. The VM will try to fix the stack guard now.
    It's highly recommended that you fix the library with 'execstack -c <libfile>', or link it with '-z noexecstack'.

    WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable

These errors are due to us using Raspbian. We could solve it by recompiling the source code, or we can simply hide the warnings for the time being:

`/opt/hadoop/etc/hadoop/hadoop-env.sh`:

    export HADOOP_OPTS="-XX:-PrintWarnings –Djava.net.preferIPv4Stack=true"

`~/.bashrc`:

    export HADOOP_HOME_WARN_SUPPRESS=1
    export HADOOP_ROOT_LOGGER="WARN,DRFA" 

the reason this happens on our Raspberry Pis is because of a mismatch between the 32-bit runtime the Hadoop binaries were built for, and the 64-bit Raspbian version we're running. To ignore these warnings, change the line

    export HADOOP_COMMON_LIB_NATIVE_DIR=${HADOOP_PREFIX}/lib/native
    export HADOOP_OPTS="-Djava.library.path=$HADOOP_PREFIX/lib/native"

### Cluster setup

Create directories on the other PIs:

    rpic-cmd "sudo mkdir -p /opt/hadoop_tmp/hdfs"
    rpic-cmd "sudo chown pi:pi -R /opt/hadoop_tmp"
    rpic-cmd "sudo mkdir -p /opt/hadoop"
    rpic-cmd "sudo chown pi:pi /opt/hadoop"

Copy files in `/opt/hadoop` to each PI. This has to be done on the master node, so make sure you have access to the rpic-list and other commands here also:

    for pi in $(rpic-list); do rsync -avxP $HADOOP_HOME $pi:/opt; done

We also need to make sure that the hadoop and spark setup commands are also copied to `.bashrc` in each PI for the path to be set up correctly. You can use the `rpic-scp` for this.

We can now issue the following command to see if all nodes can print their hadoop version to ensure that it is installed correctly:

    rpic-cmd "hadoop version"

Now edit the following files in `/opt/hadoop/etc/hadoop`:

`core-site.xml`:

    <configuration>
    <property>
        <name>fs.default.name</name>
        <value>hdfs://rpic-master:9000</value>
    </property>
    </configuration>

`hdfs-site.xml`:

    <configuration>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>/opt/hadoop_tmp/hdfs/datanode</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>/opt/hadoop_tmp/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.replication</name>
        <value>4</value>
    </property>
    </configuration>

`mapred-site.xml`:

    <configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>yarn.app.mapreduce.am.resource.mb</name>
        <value>256</value>
    </property>
    <property>
        <name>mapreduce.map.memory.mb</name>
        <value>128</value>
    </property>
    <property>
        <name>mapreduce.reduce.memory.mb</name>
        <value>128</value>
    </property>
    </configuration> 

`yarn-site.xml`:

    <configuration>
    <property>
        <name>yarn.acl.enable</name>
        <value>0</value>
    </property>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>rpic-master</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.auxservices.mapreduce.shuffle.class</name>  
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>
    <property>
        <name>yarn.nodemanager.resource.memory-mb</name>
        <value>900</value>
    </property>
    <property>
        <name>yarn.scheduler.maximum-allocation-mb</name>
        <value>900</value>
    </property>
    <property>
        <name>yarn.scheduler.minimum-allocation-mb</name>
        <value>64</value>
    </property>
    <property>
        <name>yarn.nodemanager.vmem-check-enabled</name>
        <value>false</value>
    </property>
    </configuration>

Now make sure there are no data on the nodes:

    rpic-cmd "rm -rf /opt/hadoop_tmp/hdfs/datanode/*"
    rpic-cmd "rm -rf /opt/hadoop_tmp/hdfs/namenode/*"

We now specify which node should be the NameNode and which nodes will be DataNodes. In `$HADOOP_HOME/etc/hadoop/` create one file named `master` with only the following line:

    rpic-master

In the same directory, create a file called `workers` with the following lines:

    rpic-worker-01
    rpic-worker-02
    rpic-worker-03

On all PIs, also make sure that `/etc/hosts` doesn't contain the line `127.0.0.1 piX`.

Now reboot all PIs from the local machine with the command

    rpic-reboot

On the master node, then run the command

    hdfs namenode -format -force

and boot the HDFS with

    start-dfs.sh && start-yarn.sh

Now we can create a test file an put it in the HDFS:

    echo "Hello world!" >> hello_world.txt
    hadoop fs -mkdir /test_dir
    hadoop fs -put ./hello_world.txt /test_dir/

We can then see if it shows up with

    hadoop fs -ls /test_dir

We can also access a web interface of the system on http://rpic-master:9870 or by using the IP of the master node if you don have the alias on another machine.

We can find out test file by navigating to `Utilities -> Browse the file system` and simply searching for `/` and pressing `Go!` in the search bar.

However, you (and me) might get this error at this point:

    Error “Failed to retrieve data from /webhdfs/v1/?op=LISTSTATUS: Server Error” when using hadoop

The problem here seems to be related to the java version you are using on the master node (NameNode). In my case I am using `openjdk 11.0.7 2020-04-14`.

The solution here is to download Hadoop 2.9.2 pre-compiled binaries and copy the file `share/hadoop/yarn/lib/activation-1.1.jar` from the downloaded files to the same directory in `$HADOOP_HOME` on the name node, as this file actually seems to be missing here.

While you can download the entirety of the Hadooop 2.9.2 binaries to get this file from [here](https://hadoop.apache.org/releases.html), it might be easier to just grab the file on its own from [here](https://mvnrepository.com/artifact/javax.activation/activation/1.1.1), or using this direct link with wget on the master node:
    
    wget -c https://repo1.maven.org/maven2/javax/activation/activation/1.1.1/activation-1.1.1.jar

    cp activation-1.1.jar /opt/hadoop/share/hadoop/yarn/lib/

Now just restart with

    stop-dfs.sh
    stop-yarn.sh
    start-dfs.sh
    start-yarn.sh

After reloading the web interface, you should now be able to browse the HDFS without the error!

