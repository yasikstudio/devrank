package com.yasikstudio.devrank.rank;

import static com.yasikstudio.devrank.rank.Message.*;

import java.io.IOException;
import java.util.Collection;
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
    int folNumOutEdges = sum(self.getFollowings().values());
    int actNumOutEdges = sum(self.getActivities().values());

    if (getSuperstep() > 0) {
      double folDevrank = 0;
      double actDevrank = 0;

      for (Message m : messages) {
        switch (m.getType()) {
        case FOLLOWING:
          folDevrank += m.getDevrank();
          break;
        case ACTIVITY:
          actDevrank += m.getDevrank();
          break;
        }
      }

      // calculate with PageRank algorithm
      self.setFollowingValue((0.15f / getTotalNumVertices()) + (0.85f * folDevrank));
      self.setActivityValue((0.15f / getTotalNumVertices()) + (0.85f * actDevrank));

      // store my value
      setValue(self);
    }

    if (getSuperstep() < k) {
      sendMsgTo(self.getFollowings(), FOLLOWING, self.getFollowingValue(),
          folNumOutEdges);
      sendMsgTo(self.getActivities(), ACTIVITY, self.getActivityValue(),
          actNumOutEdges);
    } else {
      voteToHalt();
    }
  }

  private void sendMsgTo(Map<String, Integer> targets, int type,
      double totalValue, int vertices) {
    double v = (vertices != 0) ? (totalValue / vertices) : 0;
    for (Map.Entry<String, Integer> target : targets.entrySet()) {
      sendMessage(new Text(target.getKey()),
          new Message(type, v * target.getValue()));
    }
  }

  private int sum(Collection<Integer> values) {
    int sum = 0;
    for (int v : values) {
      sum += v;
    }
    return sum;
  }

}
