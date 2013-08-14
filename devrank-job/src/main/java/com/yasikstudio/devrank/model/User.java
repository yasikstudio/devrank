package com.yasikstudio.devrank.model;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.hadoop.io.Writable;

public class User implements Writable {
  private String uid;
  private List<Weight> followings;
  private List<Weight> forks;
  private List<Weight> pulls;
  private List<Weight> stars;
  private List<Weight> watchs;

  @Override
  public void readFields(DataInput input) throws IOException {
    uid = input.readUTF();
    followings = readWeights(input);
    forks = readWeights(input);
    pulls = readWeights(input);
    stars = readWeights(input);
    watchs = readWeights(input);
  }

  @Override
  public void write(DataOutput output) throws IOException {
    output.writeUTF(uid);
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
}
