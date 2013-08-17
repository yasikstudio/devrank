package com.yasikstudio.devrank.rank;

import java.io.IOException;

import org.apache.giraph.graph.BasicVertex;
import org.apache.giraph.lib.TextVertexOutputFormat.TextVertexWriter;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.RecordWriter;

public class DeveloperRankVertexWriter extends
    TextVertexWriter<Text, UserVertexValue, FloatWritable> {

  public DeveloperRankVertexWriter(RecordWriter<Text, Text> lineRecordWriter) {
    super(lineRecordWriter);
  }

  @Override
  public void writeVertex(
      BasicVertex<Text, UserVertexValue, FloatWritable, ?> vertex)
      throws IOException, InterruptedException {

    UserVertexValue value = vertex.getVertexValue();

    StringBuilder results = new StringBuilder();
    results.append(vertex.getVertexId().toString());
    results.append(",");
    results.append(String.format("%.30f", value.getFollowingValue()));
    results.append(",");
    results.append(String.format("%.30f", value.getActivityValue()));

    getRecordWriter().write(new Text(results.toString()), null);
  }

}
