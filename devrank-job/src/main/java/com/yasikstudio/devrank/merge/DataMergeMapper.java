package com.yasikstudio.devrank.merge;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class DataMergeMapper extends
    Mapper<LongWritable, Text, Text, UserRecord> {

  @Override
  protected void map(LongWritable key, Text value, Context context)
      throws IOException, InterruptedException {
    String line = value.toString();
    if (line.isEmpty() || !line.contains("|")) {
      throw new IllegalArgumentException(
          "line is empty or not contain seperator: " + line);
    }

    UserRecord user = new UserRecord();
    char type = line.charAt(0);
    String[] data = line.split("\\|", -1);
    if (data.length <= 2) {
      throw new IllegalArgumentException("splitted data is so small: " + line);
    }

    user.setUid(data[1]);

    if (type == 'U' && data.length == 4) {
      // U|uid|follow_id1,follow_id2,follow_id3|fork_id4,fork_id5,fork_id6
      String[] followings = data[2].split(",");
      String[] forks = data[3].split(",");
      user.setFollowings(newWeightList(followings, 1));
      user.setForks(newWeightList(forks, 1));
    } else if (type == 'P' && data.length == 4) {
      // P|uid|owner_uid|count
      String targetUid = data[2];
      int count = Integer.parseInt(data[3]);
      user.setPulls(newWeightList(targetUid, count));
    } else if (type == 'S' && data.length == 3) {
      // S|uid|owner_uid
      String targetUid = data[2];
      user.setStars(newWeightList(targetUid, 1));
    } else if (type == 'W' && data.length == 3) {
      // W|uid|owner_uid
      String targetUid = data[2];
      user.setWatchs(newWeightList(targetUid, 1));
    } else {
      throw new IllegalArgumentException("bad line: " + line);
    }

    context.write(new Text(user.getUid()), user);
  }

  private List<Weight> newWeightList(String id, int count) {
    List<Weight> list = new ArrayList<Weight>();
    list.add(new Weight(id, count));
    return list;
  }

  private List<Weight> newWeightList(String[] ids, int count) {
    List<Weight> list = new ArrayList<Weight>();
    for (String id : ids) {
      list.add(new Weight(id, count));
    }
    return list;
  }
}
