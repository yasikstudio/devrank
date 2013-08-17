devrank-job
===========

This is a Giraph based Job project for DeveloperRank.


Prerequisites
-------------

You needs Apache Maven 3.0.4 or higher. Download it at follow link.
http://maven.apache.org/

And, `devrank-job` needs apache-giraph-0.1.0 release version. You can install
using follow commands.

    git clone https://github.com/apache/giraph.git
    cd giraph
    git checkout tags/release-0.1.0
    mvn install -Dmaven.test.skip=true


Build
-----

You can build devrank-job using Maven. just `mvn package`. It's done.

    mvn package


Getting input data
------------------

You can get data using `devrank-crawler`.

    ./ghcrawler.py

Or, you can get test data.

    wget http://static.jong10.net/jong10/data/gh_20130302_test.log


And, upload data to HDFS.

    hadoop fs -mkdir /user/YOUR_LINUX_ID/test1/input
    hadoop fs -put gh.log /user/YOUR_LINUX_ID/test1/input/input.log


And, make output directory. before running.

    hadoop fs -mkdir /user/YOUR_LINUX_ID/test1/output



How to run this
---------------

You needs installed Hadoop cluster. (You can use pseudo-distributed mode)

    hadoop jar devrank-0.0.1-jar-with-dependencies.jar -w 1 -i /user/YOUR_LINUX_ID/test1/input/input.log -o /user/YOUR_LINUX_ID/test1/output


Getting output
--------------

You can show output files using follow commands. The part-m-xxxxx are output.
For examples, (in this case, the `YOUR_LINUX_ID` is `jong10`.)

    $ bin/hadoop fs -lsr /user/jong10/test1/output
    -rw-r--r--   1 jong10 supergroup          0 2013-03-03 23:13 /user/jong10/test1/output/_SUCCESS
    drwxr-xr-x   - jong10 supergroup          0 2013-03-03 23:13 /user/jong10/test1/output/_logs
    drwxr-xr-x   - jong10 supergroup          0 2013-03-03 23:13 /user/jong10/test1/output/_logs/history
    -rw-r--r--   1 jong10 supergroup      17958 2013-03-03 23:13 /user/jong10/test1/output/_logs/history/job_201303032306_0001_1362320010028_jong10_com.yasikstudio.devrank.DeveloperRankRunner
    -rw-r--r--   1 jong10 supergroup      23190 2013-03-03 23:13 /user/jong10/test1/output/_logs/history/job_201303032306_0001_conf.xml
    -rw-r--r--   1 jong10 supergroup    2535149 2013-03-03 23:13 /user/jong10/test1/output/part-m-00001


And you can check head of data.

    hadoop fs -cat /user/YOUR_LINUX_ID/test1/output/* | head

Or, getting all data to current local directory.

    hadoop fs -get /user/YOUR_LINUX_ID/test1/output/part-* .
