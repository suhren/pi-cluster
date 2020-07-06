import pyspark
import random
import os

# If we are only running locally on ONE single node
# sc = pyspark.SparkContext(master='local[*]', appName='pi-estimation')

# If we are running on the entire cluster and letting YARN distribute the work
# sc = pyspark.SparkContext(master='yarn', appName='pi-estimation')

# If we are running on the entire cluster and letting YARN distribute the work

#os.environ['HADOOP_CONF_DIR'] = '~/hadoop_conf/'
#os.environ['YARN_CONF_DIR'] = '~/hadoop_conf/'

#print(os.environ['HADOOP_CONF_DIR'])
#print(os.environ['YARN_CONF_DIR'])

#sc = pyspark.SparkContext(master='yarn', appName='pi-estimation')
sc = pyspark.SparkContext(master='yarn')

NUM_SAMPLES = 1000000

def inside(p):
    x, y = random.random(), random.random()
    return x*x + y*y < 1

count = sc.parallelize(range(0, NUM_SAMPLES)) \
             .filter(inside).count()

print('Pi is roughly %f' % (4.0 * count / NUM_SAMPLES))