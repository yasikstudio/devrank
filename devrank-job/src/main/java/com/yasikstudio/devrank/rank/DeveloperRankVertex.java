package com.yasikstudio.devrank.rank;

import java.io.IOException;
import java.util.Iterator;

import org.apache.giraph.graph.EdgeListVertex;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;

public class DeveloperRankVertex extends
    EdgeListVertex<Text, DoubleWritable, FloatWritable, DoubleWritable> {

  private long k;

  @Override
  public void setConf(Configuration conf) {
    this.k = conf.getLong("superstep", 10L);
    super.setConf(conf);
  }

  @Override
  public void compute(Iterator<DoubleWritable> messages) throws IOException {
    if (getSuperstep() > 0) {
      double pageRank = 0;
      while (messages.hasNext()) {
        pageRank += messages.next().get();
      }
      DoubleWritable vertexValue = new DoubleWritable(
        (0.15f / getNumVertices()) + 0.85f * pageRank);
      setVertexValue(vertexValue);
    }

    if (getSuperstep() < k) {
      sendMsgToAllEdges(new DoubleWritable(
        getVertexValue().get() / getNumOutEdges()));
    } else {
      voteToHalt();
    }
  }

}
