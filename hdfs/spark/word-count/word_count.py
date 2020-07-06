import pyspark
import shutil

# If we are only running locally on ONE single node
# sc = pyspark.SparkContext(master='local[*]', appName='word-count')

# If we are running on the entire cluster and letting YARN distribute the work
sc = pyspark.SparkContext(master='yarn', appName='word-count')

text_file = sc.textFile('big.txt')
counts = text_file.flatMap(lambda line: line.split(' ')) \
             .map(lambda word: (word, 1)) \
             .reduceByKey(lambda a, b: a + b)

shutil.rmtree('counts', ignore_errors=True)
counts.saveAsTextFile('counts')