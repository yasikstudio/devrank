package com.yasikstudio.devrank;

import java.io.IOException;

import org.apache.giraph.graph.BasicVertex;
import org.apache.giraph.lib.TextVertexOutputFormat.TextVertexWriter;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.RecordWriter;

public class DeveloperRankVertexWriter extends
    TextVertexWriter<Text, DoubleWritable, FloatWritable> {

  public DeveloperRankVertexWriter(RecordWriter<Text, Text> lineRecordWriter) {
    super(lineRecordWriter);
  }

  @Override
  public void writeVertex(
      BasicVertex<Text, DoubleWritable, FloatWritable, ?> vertex)
      throws IOException, InterruptedException {

    StringBuilder results = new StringBuilder();
    results.append(vertex.getVertexId().toString());
    results.append(",");
    double devRank = vertex.getVertexValue().get();
    results.append(String.format("%.30f", devRank));

    getRecordWriter().write(new Text(results.toString()), null);
  }

}
