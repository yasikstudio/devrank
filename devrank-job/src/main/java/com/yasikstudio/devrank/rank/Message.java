package com.yasikstudio.devrank.rank;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

import org.apache.hadoop.io.Writable;

public class Message implements Writable {
  public static final int FOLLOWING = 0;
  public static final int ACTIVITY = 1;

  private int type;
  private double devrank;

  public Message() {
  }

  public Message(int type, double devrank) {
    this.type = type;
    this.devrank = devrank;
  }

  @Override
  public void readFields(DataInput input) throws IOException {
    type = input.readInt();
    devrank = input.readDouble();
  }

  @Override
  public void write(DataOutput output) throws IOException {
    output.writeInt(type);
    output.writeDouble(devrank);
  }

  public int getType() {
    return type;
  }

  public void setType(int type) {
    this.type = type;
  }

  public double getDevrank() {
    return devrank;
  }

  public void setDevrank(double devrank) {
    this.devrank = devrank;
  }

  @Override
  public int hashCode() {
    final int prime = 31;
    int result = 1;
    long temp;
    temp = Double.doubleToLongBits(devrank);
    result = prime * result + (int) (temp ^ (temp >>> 32));
    result = prime * result + type;
    return result;
  }

  @Override
  public boolean equals(Object obj) {
    if (this == obj)
      return true;
    if (obj == null)
      return false;
    if (getClass() != obj.getClass())
      return false;
    Message other = (Message) obj;
    if (Double.doubleToLongBits(devrank) != Double
        .doubleToLongBits(other.devrank))
      return false;
    if (type != other.type)
      return false;
    return true;
  }

  @Override
  public String toString() {
    return "Message [type=" + type + ", devrank=" + devrank + "]";
  }
}
