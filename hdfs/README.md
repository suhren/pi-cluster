# Hadoop File System (HDFS)

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
Add the directory to `$PATH` by editing `~/.bashrc` and adding

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
    
At a later stage, I also got the following error:

    OpenJDK Server VM warning: You have loaded library /opt/hadoop/lib/native/libhadoop.so.1.0.0 which might have disabled stack guard. The VM will try to fix the stack guard now.
    It's highly recommended that you fix the library with 'execstack -c <libfile>', or link it with '-z noexecstack'.

I fixed this by also adding these lines to `.bashrc.sh` (https://gist.github.com/ruo91/7154697 and https://stackoverflow.com/questions/19943766/hadoop-unable-to-load-native-hadoop-library-for-your-platform-warning):

    export HADOOP_COMMON_LIB_NATIVE_DIR=${HADOOP_PREFIX}/lib/native
    export HADOOP_OPTS="-Djava.library.path=$HADOOP_PREFIX/lib/native"
    
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