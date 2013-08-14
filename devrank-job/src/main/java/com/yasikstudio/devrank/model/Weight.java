package com.yasikstudio.devrank.model;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

import org.apache.hadoop.io.Writable;

public class Weight implements Writable {
  private String id;
  private int count;

  public String getId() {
    return id;
  }
  public void setId(String uid) {
    this.id = uid;
  }
  public int getCount() {
    return count;
  }
  public void setCount(int count) {
    this.count = count;
  }

  @Override
  public void readFields(DataInput input) throws IOException {
    id = input.readUTF();
    count = input.readInt();
  }
  @Override
  public void write(DataOutput output) throws IOException {
    output.writeUTF(id);
    output.writeInt(count);
  }
}
