devrank-esclient
================

Build
-----

You can build devrank-esclient-java using Maven. just `mvn package`. It's done.

    mvn package

Run
---

You can send existing data to `ElasticSearch`.

    java -jar target/devrank-esclient-0.2.0-jar-with-dependencies.jar localhost:9200 part-m-00001
