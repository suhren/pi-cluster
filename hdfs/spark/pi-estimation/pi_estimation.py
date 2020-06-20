import pyspark
import random

# If we are only running locally on ONE single node
# sc = pyspark.SparkContext(master='local[*]', appName='pi-estimation')

# If we are running on the entire cluster and letting YARN distribute the work
sc = pyspark.SparkContext(master='yarn-client', appName='pi-estimation')

NUM_SAMPLES = 1000000

def inside(p):
    x, y = random.random(), random.random()
    return x*x + y*y < 1

count = sc.parallelize(xrange(0, NUM_SAMPLES)) \
             .filter(inside).count()

print('Pi is roughly %f' % (4.0 * count / NUM_SAMPLES))