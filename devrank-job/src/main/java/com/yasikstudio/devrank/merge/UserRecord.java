package com.yasikstudio.devrank.merge;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.io.Writable;

public class UserRecord implements Writable {
  private String uid;
  private boolean user;
  private List<Weight> followings;
  private List<Weight> forks;
  private List<Weight> pulls;
  private List<Weight> stars;
  private List<Weight> watchs;

  public UserRecord() {
    uid = "";
    user = false;
    followings = new ArrayList<Weight>();
    forks = new ArrayList<Weight>();
    pulls = new ArrayList<Weight>();
    stars = new ArrayList<Weight>();
    watchs = new ArrayList<Weight>();
  }

  @Override
  public void readFields(DataInput input) throws IOException {
    uid = input.readUTF();
    user = input.readBoolean();
    followings = readWeights(input);
    forks = readWeights(input);
    pulls = readWeights(input);
    stars = readWeights(input);
    watchs = readWeights(input);
  }

  @Override
  public void write(DataOutput output) throws IOException {
    output.writeUTF(uid);
    output.writeBoolean(user);
    writeWeights(output, followings);
    writeWeights(output, forks);
    writeWeights(output, pulls);
    writeWeights(output, stars);
    writeWeights(output, watchs);
  }

  private List<Weight> readWeights(DataInput input) throws IOException {
    List<Weight> data = new ArrayList<Weight>();
    int size = input.readInt();
    for (int i = 0; i < size; i++) {
      Weight r = new Weight();
      r.readFields(input);
      data.add(r);
    }
    return data;
  }

  private void writeWeights(DataOutput output, List<Weight> data)
      throws IOException {
    output.writeInt(data.size());
    for (Weight r : data) {
      r.write(output);
    }
  }

  public String getUid() {
    return uid;
  }

  public void setUid(String uid) {
    this.uid = uid;
  }

  public boolean isUser() {
    return user;
  }

  public void setUser(boolean user) {
    this.user = user;
  }

  public List<Weight> getFollowings() {
    return followings;
  }

  public void setFollowings(List<Weight> followings) {
    this.followings = followings;
  }

  public List<Weight> getForks() {
    return forks;
  }

  public void setForks(List<Weight> forks) {
    this.forks = forks;
  }

  public List<Weight> getPulls() {
    return pulls;
  }

  public void setPulls(List<Weight> pulls) {
    this.pulls = pulls;
  }

  public List<Weight> getStars() {
    return stars;
  }

  public void setStars(List<Weight> stars) {
    this.stars = stars;
  }

  public List<Weight> getWatchs() {
    return watchs;
  }

  public void setWatchs(List<Weight> watchs) {
    this.watchs = watchs;
  }
}
