package com.yasikstudio.devrank.merge;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

import org.apache.hadoop.io.Writable;

public class Weight implements Writable {
  private String id;
  private int count;

  public Weight() {
  }

  public Weight(String id, int count) {
    this.id = id;
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

  public String getId() {
    return id;
  }

  public void setId(String id) {
    this.id = id;
  }

  public int getCount() {
    return count;
  }

  public void setCount(int count) {
    this.count = count;
  }

  @Override
  public String toString() {
    return "Weight [id=" + id + ", count=" + count + "]";
  }

  @Override
  public int hashCode() {
    final int prime = 31;
    int result = 1;
    result = prime * result + count;
    result = prime * result + ((id == null) ? 0 : id.hashCode());
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
    Weight other = (Weight) obj;
    if (count != other.count)
      return false;
    if (id == null) {
      if (other.id != null)
        return false;
    } else if (!id.equals(other.id))
      return false;
    return true;
  }
}
