package com.yasikstudio.devrank.rank;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

import org.apache.hadoop.io.Writable;

public class Message implements Writable {

  private double devrankValue;

  public Message() {
  }

  public Message(double devrankValue) {
    this.devrankValue = devrankValue;
  }

  @Override
  public void readFields(DataInput input) throws IOException {
    devrankValue = input.readDouble();
  }

  @Override
  public void write(DataOutput output) throws IOException {
    output.writeDouble(devrankValue);
  }

  public double getDevrankValue() {
    return devrankValue;
  }

  public void setDevrank(double devrankValue) {
    this.devrankValue = devrankValue;
  }

  @Override
  public int hashCode() {
    final int prime = 31;
    int result = 1;
    long temp;
    temp = Double.doubleToLongBits(devrankValue);
    result = prime * result + (int) (temp ^ (temp >>> 32));
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
    if (Double.doubleToLongBits(devrankValue) != Double
        .doubleToLongBits(other.devrankValue))
      return false;
    return true;
  }

  @Override
  public String toString() {
    return "Message [devrankValue=" + devrankValue + "]";
  }
}
