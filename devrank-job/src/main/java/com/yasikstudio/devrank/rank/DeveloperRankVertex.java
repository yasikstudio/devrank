package com.yasikstudio.devrank.rank;

import java.io.IOException;
import java.util.Map;

import org.apache.giraph.graph.Vertex;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;

public class DeveloperRankVertex extends
    Vertex<Text, UserVertexValue, FloatWritable, Message> {

  @Override
  public void compute(Iterable<Message> messages) throws IOException {
    int k = getConf().getInt("superstep", 0);
    UserVertexValue self = getValue();
    long outEdges = self.getOutEdges();

    if (getSuperstep() > 0) {
      double sum = 0;
      for (Message m : messages) {
        sum += m.getDevrankValue();
      }

      // calculate with PageRank algorithm using countOfOutWeight.
      // do not use getTotalNumvertices() for weighted edges.
      self.setValue((0.15f / outEdges) + (0.85f * sum));

      // store my value
      setValue(self);
    }

    if (getSuperstep() < k) {
      // TODO
      // double v = (outEdges != 0) ? (self.getValue() / outEdges) : 0;
      // sendMessageToAllEdges(new Message(v));

      sendMsgTo(self.getAllEdges(), self.getValue(), self.getOutEdges());
    } else {
      voteToHalt();
    }
  }

  private void sendMsgTo(Map<String, Long> targets, double totalValue,
      long vertices) {
    double v = (vertices != 0) ? (totalValue / vertices) : 0;
    for (Map.Entry<String, Long> target : targets.entrySet()) {
      sendMessage(new Text(target.getKey()), new Message(v * target.getValue()));
    }
  }
}
