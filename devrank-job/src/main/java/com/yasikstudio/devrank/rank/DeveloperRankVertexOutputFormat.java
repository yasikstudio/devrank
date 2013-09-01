package com.yasikstudio.devrank.rank;

import java.io.IOException;

import org.apache.giraph.graph.Vertex;
import org.apache.giraph.io.formats.TextVertexOutputFormat;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.TaskAttemptContext;

public class DeveloperRankVertexOutputFormat extends
    TextVertexOutputFormat<Text, UserVertexValue, FloatWritable> {

  @Override
  public TextVertexWriter createVertexWriter(TaskAttemptContext context)
      throws IOException, InterruptedException {
    return new DeveloperRankVertexWriter();
  }

  public class DeveloperRankVertexWriter extends TextVertexWriter {
    @Override
    public void writeVertex(
        Vertex<Text, UserVertexValue, FloatWritable, ?> vertex)
        throws IOException, InterruptedException {

      String uid = vertex.getId().toString();
      UserVertexValue value = vertex.getValue();
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

      // write to HDFS
      getRecordWriter().write(new Text(results.toString()), null);
    }

  }
}
