package com.yasikstudio.devrank.rank;

import java.io.IOException;
import java.util.Map;
import java.util.Set;

import org.apache.giraph.graph.BasicVertex;
import org.apache.giraph.graph.BspUtils;
import org.apache.giraph.lib.TextVertexInputFormat.TextVertexReader;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.RecordReader;
import org.hsqldb.lib.StringUtil;

import com.google.common.collect.Maps;
import com.google.common.collect.Sets;

public class DeveloperRankVertexReader extends
    TextVertexReader<Text, UserVertexValue, FloatWritable, Message> {

  public DeveloperRankVertexReader(
      RecordReader<LongWritable, Text> lineRecordReader) {
    super(lineRecordReader);
  }

  @Override
  public BasicVertex<Text, UserVertexValue, FloatWritable, Message> getCurrentVertex()
      throws IOException, InterruptedException {

    BasicVertex<Text, UserVertexValue, FloatWritable, Message> vertex = BspUtils
        .<Text, UserVertexValue, FloatWritable, Message> createVertex(getContext()
            .getConfiguration());

    // input values:
    // id|followings...|forks...|pull...|star...|watch...
    // 999212|14953:1,931534:1|1445542:1,999212:10|999212:1,145585:1||931534:2,1589355:1,575576:1,1206239:1,71561:2,333745:1
    // 999255|||||333745:1

    // read, parse and setup.
    Text line = getRecordReader().getCurrentValue();
    String[] items = line.toString().split("\\|", -1);
    Text uid = new Text(items[0]);
    Map<String, Integer> followings = parseEdges(items[1]);
    Map<String, Integer> activities = parseEdges(items[2], items[3], items[4],
        items[5]);

    // setup initialized vertex value
    UserVertexValue vertexValue = new UserVertexValue(followings, activities);

    // setup edges
    Set<String> ids = Sets.newHashSet();
    ids.addAll(followings.keySet());
    ids.addAll(activities.keySet());
    Map<Text, FloatWritable> edges = generateEdges(ids);

    // initialize vertex
    vertex.initialize(uid, vertexValue, edges, null);

    return vertex;
  }

  @Override
  public boolean nextVertex() throws IOException, InterruptedException {
    return getRecordReader().nextKeyValue();
  }

  private Map<Text, FloatWritable> generateEdges(Set<String> ids) {
    Map<Text, FloatWritable> edges = Maps.newHashMap();
    for (String targetId : ids.toArray(new String[0])) {
      if (targetId != null && !"".equals(targetId)) {
        edges.put(new Text(targetId), new FloatWritable(1.0f));
      }
    }
    return edges;
  }

  private Map<String, Integer> parseEdges(String... data) {
    Map<String, Integer> map = Maps.newHashMap();
    for (String category : data) {
      for (String item : category.split(",")) {
        if (!StringUtil.isEmpty(item)) {
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
