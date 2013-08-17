package com.yasikstudio.devrank.merge;

import java.io.IOException;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class DataMergeCombiner extends Reducer<Text, UserRecord, Text, UserRecord> {

  @Override
  protected void reduce(Text key, Iterable<UserRecord> values, Context context)
      throws IOException, InterruptedException {
    UserRecord user = new UserRecord();
    user.setUid(key.toString());

    for (UserRecord u : values) {
      MergeUtils.merge(user, u);
    }

    context.write(key, user);
  }

}
