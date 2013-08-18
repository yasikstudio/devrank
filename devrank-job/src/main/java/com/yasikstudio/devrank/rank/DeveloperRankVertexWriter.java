package com.yasikstudio.devrank.rank;

import java.io.IOException;

import org.apache.giraph.graph.BasicVertex;
import org.apache.giraph.lib.TextVertexOutputFormat.TextVertexWriter;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.RecordWriter;

import com.yasikstudio.devrank.util.ESClient;

public class DeveloperRankVertexWriter extends
    TextVertexWriter<Text, UserVertexValue, FloatWritable> {

  private ESClient esClient;

  public DeveloperRankVertexWriter(RecordWriter<Text, Text> lineRecordWriter,
      ESClient esClient) {
    super(lineRecordWriter);
    this.esClient = esClient;
  }

  @Override
  public void writeVertex(
      BasicVertex<Text, UserVertexValue, FloatWritable, ?> vertex)
      throws IOException, InterruptedException {

    String uid = vertex.getVertexId().toString();
    UserVertexValue value = vertex.getVertexValue();
    double followingValue = value.getFollowingValue();
    double activityValue = value.getActivityValue();

    StringBuilder results = new StringBuilder();
    results.append(uid);
    results.append(",");
    results.append(value.exists());
    results.append(",");
    results.append(String.format("%.30f", followingValue));
    results.append(",");
    results.append(String.format("%.30f", activityValue));

    // send to ElasticSearch
    if (esClient != null) {
      esClient.update(uid, followingValue + activityValue);
    }

    // write to HDFS
    getRecordWriter().write(new Text(results.toString()), null);
  }

}
