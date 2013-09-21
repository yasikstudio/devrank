package com.yasikstudio.devrank.rank;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import org.apache.giraph.edge.Edge;
import org.apache.giraph.edge.EdgeFactory;
import org.apache.giraph.graph.Vertex;
import org.apache.giraph.io.formats.TextVertexInputFormat;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.InputSplit;
import org.apache.hadoop.mapreduce.TaskAttemptContext;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;

public class DeveloperRankVertexInputFormat extends
    TextVertexInputFormat<Text, UserVertexValue, FloatWritable> {
  @Override
  public TextVertexReader createVertexReader(InputSplit split,
      TaskAttemptContext context) throws IOException {
    return new DeveloperRankVertexReader();
  }

  public class DeveloperRankVertexReader
      extends
      TextVertexInputFormat<Text, UserVertexValue, FloatWritable>.TextVertexReader {

    @Override
    public Vertex<Text, UserVertexValue, FloatWritable, ?> getCurrentVertex()
        throws IOException, InterruptedException {

      Vertex<Text, UserVertexValue, FloatWritable, ?> vertex = getConf()
          .createVertex();

      // input values:
      // id|true|followings...|forks...|pull...|star...|watch...
      // 999212|true|14953:1,931534:1|1445542:1,999212:10|999212:1,145585:1||931534:2,1589355:1,575576:1,1206239:1,71561:2,333745:1
      // 999255|false|||||333745:1

      int[] ratio = parseRatioOption(getConf().get("ratioOptions"));

      // read, parse and setup.
      Text line = getRecordReader().getCurrentValue();

      try {
        String[] items = line.toString().split("\\|", -1);
        Text uid = new Text(items[0]);
        boolean exists = Boolean.parseBoolean(items[1]);
        Map<String, Long> followings = parseEdge(items[2], ratio[0]);
        Map<String, Long> forks = parseEdge(items[3], ratio[1]);
        Map<String, Long> pulls = parseEdge(items[4], ratio[2]);
        Map<String, Long> stars = parseEdge(items[5], ratio[3]);
        Map<String, Long> watches = parseEdge(items[6], ratio[4]);

        @SuppressWarnings("unchecked")
        Map<String, Long> allEdges = merge(followings, forks, pulls, stars,
            watches);

        long outEdges = sum(allEdges);

        // setup initialized vertex value
        // TODO
//        UserVertexValue vertexValue = new UserVertexValue(exists, outEdges);
        UserVertexValue vertexValue = new UserVertexValue(exists, outEdges, allEdges);

        // setup edges
        List<Edge<Text, FloatWritable>> edges = generateEdges(allEdges);

        // initialize vertex
        vertex.initialize(uid, vertexValue, edges);
      } catch (Throwable t) {
        throw new IllegalArgumentException(line.toString(), t);
      }

      return vertex;
    }

    private int[] parseRatioOption(String option) {
      String[] ratioOptions = option.split(",", -1);
      int[] ratio = new int[ratioOptions.length];
      for (int i = 0; i < ratioOptions.length; i++) {
        ratio[i] = Integer.parseInt(ratioOptions[i]);
      }
      return ratio;
    }

    private Map<String, Long> parseEdge(String data, long weight) {
      Map<String, Long> map = Maps.newHashMap();
      for (String item : data.split(",")) {
        if (item != null && !"".equals(item)) {
          String[] idAndCount = item.split(":", 2);
          String id = idAndCount[0];
          long count = Integer.parseInt(idAndCount[1]);
          long prev = map.containsKey(id) ? map.get(id) : 0;
          long current = count * weight;
          map.put(id, prev + current);
        }
      }
      return map;
    }

    private Map<String, Long> merge(Map<String, Long>... allEdges) {
      Map<String, Long> merged = Maps.newHashMap();
      for (Map<String, Long> edges : allEdges) {
        for (Map.Entry<String, Long> item : edges.entrySet()) {
          String key = item.getKey();
          long oldValue = merged.containsKey(key) ? merged.get(key) : 0;
          merged.put(key, oldValue + item.getValue());
        }
      }
      return merged;
    }

    private long sum(Map<String, Long> edges) {
      long sum = 0;
      for (Map.Entry<String, Long> item : edges.entrySet()) {
        sum += item.getValue();
      }
      return sum;
    }

    private List<Edge<Text, FloatWritable>> generateEdges(
        Map<String, Long> allEdges) {
      List<Edge<Text, FloatWritable>> edges = Lists.newArrayList();
      for (Map.Entry<String, Long> e : allEdges.entrySet()) {
        edges.add(EdgeFactory.create(new Text(e.getKey()), new FloatWritable(
            1.0f)));

        // TODO
//        edges.add(EdgeFactory.create(new Text(e.getKey()), new FloatWritable(
//            (float) e.getValue())));
      }
      return edges;
    }

    @Override
    public boolean nextVertex() throws IOException, InterruptedException {
      return getRecordReader().nextKeyValue();
    }
  }
}
