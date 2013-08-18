package com.yasikstudio.devrank.rank;

import java.io.IOException;

import org.apache.giraph.graph.VertexWriter;
import org.apache.giraph.lib.TextVertexOutputFormat;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.RecordWriter;
import org.apache.hadoop.mapreduce.TaskAttemptContext;

import com.yasikstudio.devrank.util.ESClient;

public class DeveloperRankVertexOutputFormat extends
    TextVertexOutputFormat<Text, UserVertexValue, FloatWritable> {

  @Override
  public VertexWriter<Text, UserVertexValue, FloatWritable> createVertexWriter(
      TaskAttemptContext context) throws IOException, InterruptedException {

    Configuration conf = context.getConfiguration();
    String elasticSearchAddress = conf.get("elasticSearch");
    ESClient esClient = null;
    if (elasticSearchAddress != null || "".equals(elasticSearchAddress)) {
      esClient = new ESClient(elasticSearchAddress);
    }

    RecordWriter<Text, Text> recordWriter =
        textOutputFormat.getRecordWriter(context);
    return new DeveloperRankVertexWriter(recordWriter, esClient);
  }

}
