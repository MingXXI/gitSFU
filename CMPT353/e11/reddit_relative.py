import sys
from pyspark.sql import SparkSession, functions, types

spark = SparkSession.builder.appName('reddit relative scores').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 5) # make sure we have Python 3.5+
assert spark.version >= '2.3' # make sure we have Spark 2.3+

schema = types.StructType([ # commented-out fields won't be read
    #types.StructField('archived', types.BooleanType(), False),
    types.StructField('author', types.StringType(), False),
    #types.StructField('author_flair_css_class', types.StringType(), False),
    #types.StructField('author_flair_text', types.StringType(), False),
    #types.StructField('body', types.StringType(), False),
    #types.StructField('controversiality', types.LongType(), False),
    #types.StructField('created_utc', types.StringType(), False),
    #types.StructField('distinguished', types.StringType(), False),
    #types.StructField('downs', types.LongType(), False),
    #types.StructField('edited', types.StringType(), False),
    #types.StructField('gilded', types.LongType(), False),
    #types.StructField('id', types.StringType(), False),
    #types.StructField('link_id', types.StringType(), False),
    #types.StructField('name', types.StringType(), False),
    #types.StructField('parent_id', types.StringType(), True),
    #types.StructField('retrieved_on', types.LongType(), False),
    types.StructField('score', types.LongType(), False),
    #types.StructField('score_hidden', types.BooleanType(), False),
    types.StructField('subreddit', types.StringType(), False),
    #types.StructField('subreddit_id', types.StringType(), False),
    #types.StructField('ups', types.LongType(), False),
])


def main(in_directory, out_directory):
    comments = spark.read.json(in_directory, schema=schema).cache()

    # TODO
    # get average subreddit score
    average = comments.groupby('subreddit').avg().cache()
    # filter average score > 0
    average = average.filter(average['avg(score)'] > 0)

    # merge with original table
    # average = average.join(comments,'subreddit')

    # merge with original table (with broadcast)
    average = functions.broadcast(average)
    average = average.join(comments,'subreddit')

    # add column 'relative_score'
    average = average.withColumn('relative_score', average['score']/average['avg(score)'])
    # get max score
    average = average.groupby('subreddit').max().cache()

    # join with original table
    # average = average.join(comments, 'subreddit')

    # join with original table (with broadcast)
    average = functions.broadcast(average)
    average = average.join(comments, 'subreddit')

    # filter tuple with max score
    average = average.filter(average['score']==average['max(score)'])
    
    best_author = average.select(average['subreddit'], average['author'], average['max(relative_score)'].alias('rel_score'))
    # best_author = max_by_subreddit.join(functions.broadcast(average), 'subreddit', 'inner')

    best_author.write.json(out_directory, mode='overwrite')


if __name__=='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)
