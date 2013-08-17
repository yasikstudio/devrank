package com.yasikstudio.devrank.rank;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.apache.hadoop.io.Writable;

import com.google.common.collect.Maps;

public class UserVertexValue implements Writable {
  private Map<String, Integer> followings;
  private Map<String, Integer> activities;
  private double followingValue;
  private double activityValue;

  public UserVertexValue() {
    this(new HashMap<String, Integer>(), new HashMap<String, Integer>());
  }

  public UserVertexValue(Map<String, Integer> followings,
      Map<String, Integer> activities) {
    this.followings = followings;
    this.activities = activities;
    this.followingValue = 0;
    this.activityValue = 0;
  }

  @Override
  public void readFields(DataInput input) throws IOException {
    followings = readMap(input);
    activities = readMap(input);
    followingValue = input.readDouble();
    activityValue = input.readDouble();
  }

  @Override
  public void write(DataOutput output) throws IOException {
    writeMap(output, followings);
    writeMap(output, activities);
    output.writeDouble(followingValue);
    output.writeDouble(activityValue);
  }

  private Map<String, Integer> readMap(DataInput input) throws IOException {
    Map<String, Integer> data = Maps.newHashMap();
    int size = input.readInt();
    for (int i = 0; i < size; i++) {
      String key = input.readUTF();
      int value = input.readInt();
      data.put(key, value);
    }
    return data;
  }

  private void writeMap(DataOutput output, Map<String, Integer> data)
      throws IOException {
    output.writeInt(data.size());
    for (Map.Entry<String, Integer> item : data.entrySet()) {
      output.writeUTF(item.getKey());
      output.writeInt(item.getValue().intValue());
    }
  }

  public Map<String, Integer> getFollowings() {
    return followings;
  }

  public void setFollowings(Map<String, Integer> followings) {
    this.followings = followings;
  }

  public Map<String, Integer> getActivities() {
    return activities;
  }

  public void setActivities(Map<String, Integer> activities) {
    this.activities = activities;
  }

  public double getFollowingValue() {
    return followingValue;
  }

  public void setFollowingValue(double followingValue) {
    this.followingValue = followingValue;
  }

  public double getActivityValue() {
    return activityValue;
  }

  public void setActivityValue(double activityValue) {
    this.activityValue = activityValue;
  }
}
