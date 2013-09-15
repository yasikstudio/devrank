package com.yasikstudio.devrank.rank;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.apache.hadoop.io.Writable;

import com.google.common.collect.Maps;

public class UserVertexValue implements Writable {
  private boolean exists;
  private double value;
  private long outEdges;
  private Map<String, Long> allEdges;

  public UserVertexValue() {
    this(false, 0, new HashMap<String, Long>());
  }

  public UserVertexValue(boolean exists, long outEdges) {
    this.exists = exists;
    this.value = 0;
    this.outEdges = outEdges;
  }

  public UserVertexValue(boolean exists, long outEdges,
      Map<String, Long> allEdges) {
    this.exists = exists;
    this.value = 0;
    this.outEdges = outEdges;
    this.allEdges = allEdges;
  }

  @Override
  public void readFields(DataInput input) throws IOException {
    exists = input.readBoolean();
    value = input.readDouble();
    outEdges = input.readLong();
    allEdges = readMap(input);
  }

  @Override
  public void write(DataOutput output) throws IOException {
    output.writeBoolean(exists);
    output.writeDouble(value);
    output.writeLong(outEdges);
    writeMap(output, allEdges);
  }

  public boolean exists() {
    return exists;
  }

  public void setExists(boolean exists) {
    this.exists = exists;
  }

  public double getValue() {
    return value;
  }

  public void setValue(double value) {
    this.value = value;
  }

  public long getOutEdges() {
    return outEdges;
  }

  public void setOutEdges(long outEdges) {
    this.outEdges = outEdges;
  }

  public Map<String, Long> getAllEdges() {
    return allEdges;
  }

  public void setAllEdges(Map<String, Long> allEdges) {
    this.allEdges = allEdges;
  }

  private Map<String, Long> readMap(DataInput input) throws IOException {
    Map<String, Long> data = Maps.newHashMap();
    int size = input.readInt();
    for (int i = 0; i < size; i++) {
      String key = input.readUTF();
      long value = input.readLong();
      data.put(key, value);
    }
    return data;
  }

  private void writeMap(DataOutput output, Map<String, Long> data)
      throws IOException {
    output.writeInt(data.size());
    for (Map.Entry<String, Long> item : data.entrySet()) {
      output.writeUTF(item.getKey());
      output.writeLong(item.getValue());
    }
  }
}
