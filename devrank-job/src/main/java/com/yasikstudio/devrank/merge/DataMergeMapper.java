package com.yasikstudio.devrank.merge;

import java.io.IOException;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import com.yasikstudio.devrank.model.User;

public class DataMergeMapper extends Mapper<LongWritable, Text, Text, User> {

  @Override
  protected void map(LongWritable key, Text value, Context context)
      throws IOException, InterruptedException {
    // TODO
  }

}
