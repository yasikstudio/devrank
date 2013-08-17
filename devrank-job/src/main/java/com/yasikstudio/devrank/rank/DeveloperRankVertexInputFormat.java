package com.yasikstudio.devrank.rank;

import java.io.IOException;

import org.apache.giraph.graph.VertexReader;
import org.apache.giraph.lib.TextVertexInputFormat;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.InputSplit;
import org.apache.hadoop.mapreduce.TaskAttemptContext;

public class DeveloperRankVertexInputFormat extends
    TextVertexInputFormat<Text, UserVertexValue, FloatWritable, Message> {
  @Override
  public VertexReader<Text, UserVertexValue, FloatWritable, Message> createVertexReader(
      InputSplit split, TaskAttemptContext context) throws IOException {
    return new DeveloperRankVertexReader(textInputFormat.createRecordReader(
        split, context));
  }

}
