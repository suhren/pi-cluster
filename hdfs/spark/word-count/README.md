## Install PySpark

To install PySpark, we can simply use pip. We do however need to make sure to install the same version as the exisiting Apache Spark installation on the cluster, otherwise we might get an error like 

```
pyspark error does not exist in the jvm error when initializing SparkContext
```

when trying to run PySpark. To find our existing spark version on the master node, we can run the command

```bash
spark-submit --version
```

And we should get an output like

```
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /___/ .__/\_,_/_/ /_/\_\   version 2.4.6
      /_/
                        
Using Scala version 2.11.12, OpenJDK Server VM, 11.0.7
Branch HEAD
Compiled by user holden on 2020-05-29T23:47:51Z
Revision 807e0a484d1de767d1f02bd8a622da6450bdf940
Url https://gitbox.apache.org/repos/asf/spark.git
Type --help for more information.
```

We can then install PySpark for Python 3 matching this version with

```bash
pip3 install pyspark==2.4.6
```

or for Python 2:

```bash
pip install pyspark==2.4.6 --no-cache-dir
```

I had to use `--no-cache-dir` since I was getting a memory error when trying to install for Python 2 for some reason!