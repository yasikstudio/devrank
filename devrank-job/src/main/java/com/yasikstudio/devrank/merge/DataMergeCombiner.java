package com.yasikstudio.devrank.merge;

import java.io.IOException;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import com.yasikstudio.devrank.model.User;

public class DataMergeCombiner extends Reducer<Text, User, Text, User> {

  @Override
  protected void reduce(Text key, Iterable<User> values, Context context)
      throws IOException, InterruptedException {
    User user = new User();
    user.setUid(key.toString());

    for (User u : values) {
      MergeUtils.merge(user, u);
    }

    context.write(key, user);
  }

}
