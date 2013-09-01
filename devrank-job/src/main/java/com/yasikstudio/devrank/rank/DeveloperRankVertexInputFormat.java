package com.yasikstudio.devrank.rank;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Set;

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
import com.google.common.collect.Sets;

public class DeveloperRankVertexInputFormat
    extends TextVertexInputFormat<Text, UserVertexValue, FloatWritable> {
  @Override
  public TextVertexReader createVertexReader(
      InputSplit split, TaskAttemptContext context) throws IOException {
    return new DeveloperRankVertexReader();
  }

  public class DeveloperRankVertexReader extends
      TextVertexInputFormat<Text, UserVertexValue,
      FloatWritable>.TextVertexReader {

    @Override
    public Vertex<Text, UserVertexValue, FloatWritable, ?> getCurrentVertex()
        throws IOException, InterruptedException {

      // TODO: this getConf() is ok ?
      Vertex<Text, UserVertexValue, FloatWritable, ?> vertex =
          getConf().createVertex();

      // input values:
      // id|true|followings...|forks...|pull...|star...|watch...
      // 999212|true|14953:1,931534:1|1445542:1,999212:10|999212:1,145585:1||931534:2,1589355:1,575576:1,1206239:1,71561:2,333745:1
      // 999255|false|||||333745:1

      // read, parse and setup.
      Text line = getRecordReader().getCurrentValue();

      try {
        String[] items = line.toString().split("\\|", -1);
        Text uid = new Text(items[0]);
        boolean exists = Boolean.parseBoolean(items[1]);
        Map<String, Integer> followings = parseEdges(items[2]);
        Map<String, Integer> activities =
            parseEdges(items[3], items[4], items[5], items[6]);

        // setup initialized vertex value
        UserVertexValue vertexValue =
            new UserVertexValue(exists, followings, activities);

        // setup edges
        Set<String> ids = Sets.newHashSet();
        ids.addAll(followings.keySet());
        ids.addAll(activities.keySet());
        List<Edge<Text, FloatWritable>> edges = generateEdges(ids);

        // initialize vertex
        vertex.initialize(uid, vertexValue, edges);
      } catch (Throwable t) {
        throw new IllegalArgumentException(line.toString(), t);
      }

      return vertex;
    }

    @Override
    public boolean nextVertex() throws IOException, InterruptedException {
      return getRecordReader().nextKeyValue();
    }

    private List<Edge<Text, FloatWritable>> generateEdges(Set<String> ids) {
      Map<Text, FloatWritable> data = Maps.newHashMap();
      for (String targetId : ids.toArray(new String[0])) {
        if (targetId != null && !"".equals(targetId)) {
          data.put(new Text(targetId), new FloatWritable(1.0f));
        }
      }
      List<Edge<Text, FloatWritable>> edges = Lists.newArrayList();
      for (Map.Entry<Text, FloatWritable> entry : data.entrySet()) {
        edges.add(EdgeFactory.create(entry.getKey(), entry.getValue()));
      }
      return edges;
    }

    private Map<String, Integer> parseEdges(String... data) {
      Map<String, Integer> map = Maps.newHashMap();
      for (String category : data) {
        for (String item : category.split(",")) {
          if (item != null && !"".equals(item)) {
            String[] idAndCount = item.split(":", 2);
            String id = idAndCount[0];
            int count = Integer.parseInt(idAndCount[1]);
            if (map.containsKey(id)) {
              map.put(id, map.get(id) + count);
            } else {
              map.put(id, count);
            }
          }
        }
      }
      return map;
    }
  }
}
