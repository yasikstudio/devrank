devrank-esclient-java
=====================

Build
-----

You can build devrank-esclient-java using Maven. just `mvn package`. It's done.

    mvn package

Installation
------------

You can also install devrank-esclient-java using Maven.

    mvn install -DskipTests

Add devrank-esclient-java as a dependency to your project.

``` xml
<dependency>
  <groupId>devrank-esclient-java</groupId>¬
  <artifactId>devrank-esclient-java</artifactId>¬
  <version>0.1-SNAPSHOT</version>¬
</dependency>
```

Usage
-----

``` java
ESClient es = new ESClient("http://jweb.kr:9200", "github");

// 314555 is jweb
if (es.update(USERS_INDEX_TYPE, "314555",
    USERS_SCORE_UPDATE_SCRIPT,
    ESClient.scoreBuildToMap(3.5))) {
  System.out.println("DevRank Score update is succeeded.");
}
else {
  System.out.println("DevRank Score update is failed.");
}
```
