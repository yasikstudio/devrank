package com.yasikstudio.devrank.merge;

import java.io.IOException;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import com.yasikstudio.devrank.model.User;

public class DataMergeReducer extends Reducer<Text, User, Text, NullWritable> {

  @Override
  protected void reduce(Text key, Iterable<User> values, Context context)
      throws IOException, InterruptedException {
    // TODO
  }

}
