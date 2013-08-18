package com.yasikstudio.devrank.merge;

import java.io.IOException;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class DataMergeCombiner extends Reducer<Text, UserRecord, Text, UserRecord> {

  @Override
  protected void reduce(Text key, Iterable<UserRecord> values, Context context)
      throws IOException, InterruptedException {
    UserRecord user = new UserRecord();
    boolean existing = user.exists();
    user.setUid(key.toString());

    for (UserRecord u : values) {
      existing = existing || u.exists();
      MergeUtils.merge(user, u);
    }
    user.setExists(existing);

    // don't care about exisiting. because this is combiner.
    context.write(key, user);
  }

}
