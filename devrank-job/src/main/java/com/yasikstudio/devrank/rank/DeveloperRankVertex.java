package com.yasikstudio.devrank.rank;

import static com.yasikstudio.devrank.rank.Message.*;

import java.io.IOException;
import java.util.Collection;
import java.util.Iterator;
import java.util.Map;

import org.apache.giraph.graph.EdgeListVertex;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;

public class DeveloperRankVertex extends
    EdgeListVertex<Text, UserVertexValue, FloatWritable, Message> {

  private long k;

  @Override
  public void setConf(Configuration conf) {
    this.k = conf.getLong("superstep", 10L);
    super.setConf(conf);
  }

  @Override
  public void compute(Iterator<Message> messages) throws IOException {
    UserVertexValue self = getVertexValue();
    int folNumOutEdges = sum(self.getFollowings().values());
    int actNumOutEdges = sum(self.getActivities().values());

    if (getSuperstep() > 0) {
      double folDevrank = 0;
      double actDevrank = 0;

      while (messages.hasNext()) {
        Message m = messages.next();
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
      self.setFollowingValue((0.15f / getNumVertices()) + (0.85f * folDevrank));
      self.setActivityValue((0.15f / getNumVertices()) + (0.85f * actDevrank));

      // store my value
      setVertexValue(self);
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
      sendMsg(new Text(target.getKey()),
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
