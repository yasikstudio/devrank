package com.yasikstudio.devrank.rank;

import java.io.IOException;

import org.apache.giraph.graph.VertexWriter;
import org.apache.giraph.lib.TextVertexOutputFormat;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.RecordWriter;
import org.apache.hadoop.mapreduce.TaskAttemptContext;

public class DeveloperRankVertexOutputFormat extends
    TextVertexOutputFormat<Text, DoubleWritable, FloatWritable> {

  @Override
  public VertexWriter<Text, DoubleWritable, FloatWritable>
      createVertexWriter(TaskAttemptContext context)
          throws IOException, InterruptedException {

    RecordWriter<Text, Text> recordWriter =
        textOutputFormat.getRecordWriter(context);
    return new DeveloperRankVertexWriter(recordWriter);
  }

}
