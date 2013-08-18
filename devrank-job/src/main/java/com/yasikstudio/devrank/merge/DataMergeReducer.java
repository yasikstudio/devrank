package com.yasikstudio.devrank.merge;

import java.io.IOException;
import java.util.List;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class DataMergeReducer extends Reducer<Text, UserRecord, Text, NullWritable> {

  private static final String FIELD_SEP = "|";
  private static final String LIST_SEP = ",";
  private static final String COUNT_SEP = ":";

  @Override
  protected void reduce(Text key, Iterable<UserRecord> values, Context context)
      throws IOException, InterruptedException {
    UserRecord user = new UserRecord();
    user.setUid(key.toString());
    boolean existing = user.isUser();

    for (UserRecord u : values) {
      MergeUtils.merge(user, u);
      existing = existing || u.isUser();
    }

    user.setUser(existing);

    if (existing) {
      context.write(new Text(writeToString(user)), null);
    }
  }

  private String writeToString(UserRecord user) {
    // uid
    // |follow1:1,follow2:1
    // |fork1:1,fork2:1
    // |pull_1:324,pull_2:123
    // |star1:1,star2:1
    // |watch1:1,watch2:1

    StringBuilder out = new StringBuilder();
    out.append(user.getUid()).append(FIELD_SEP);
    appendWeightList(out, user.getFollowings()).append(FIELD_SEP);
    appendWeightList(out, user.getForks()).append(FIELD_SEP);
    appendWeightList(out, user.getPulls()).append(FIELD_SEP);
    appendWeightList(out, user.getStars()).append(FIELD_SEP);
    appendWeightList(out, user.getWatchs());

    return out.toString();
  }

  private StringBuilder appendWeightList(StringBuilder out, List<Weight> weights) {
    int size = weights.size();
    for (int i = 0; i < size; i++) {
      Weight w = weights.get(i);
      out.append(w.getId()).append(COUNT_SEP).append(w.getCount());
      if (i != size - 1) {
        out.append(LIST_SEP);
      }
    }
    return out;
  }

}
