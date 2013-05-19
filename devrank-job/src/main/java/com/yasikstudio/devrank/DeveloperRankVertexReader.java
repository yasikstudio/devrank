package com.yasikstudio.devrank;

import java.io.IOException;
import java.util.Map;

import org.apache.giraph.graph.BasicVertex;
import org.apache.giraph.graph.BspUtils;
import org.apache.giraph.lib.TextVertexInputFormat.TextVertexReader;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.RecordReader;

import com.google.common.collect.Maps;

public class DeveloperRankVertexReader extends
    TextVertexReader<Text,
        DoubleWritable, FloatWritable, DoubleWritable> {

  public DeveloperRankVertexReader(
      RecordReader<LongWritable, Text> lineRecordReader) {
    super(lineRecordReader);
  }

  @Override
  public BasicVertex<Text, DoubleWritable, FloatWritable,
      DoubleWritable> getCurrentVertex() throws IOException,
          InterruptedException {

    BasicVertex<Text, DoubleWritable, FloatWritable,
        DoubleWritable> vertex = BspUtils.<Text, DoubleWritable,
            FloatWritable, DoubleWritable>createVertex(
                getContext().getConfiguration());

    Map<Text, FloatWritable> edges = Maps.newHashMap();

    // input values
    // beonit,1.0,jong10,mooz,jmjeong,dalinaum,gochist,xiles,reeoss,raycon
    // frst1809,1.0,
    // jong10,1.0,
    // jweb,1.0,dittos,jong10,hyunsik,haven-jeon
    // raycon,1.0,jong10,beonit,reeoss
    // reeoss,1.0,jong10,beonit,realbeast,raycon,aprilhyuna,baekjh09

    // read, parse and setup.
    Text line = getRecordReader().getCurrentValue();
    String[] data = line.toString().split(",");
    Text user = new Text(data[0]);
    DoubleWritable vertexValue =
        new DoubleWritable(Double.parseDouble(data[1]));

    for (int i = 2; i < data.length; i++) {
      String v = data[i].trim();
      if (v != null && !"".equals(v)) {
        edges.put(new Text(v), new FloatWritable(1.0f));
      }
    }

    vertex.initialize(user, vertexValue, edges, null);

    return vertex;
  }

  @Override
  public boolean nextVertex() throws IOException, InterruptedException {
    return getRecordReader().nextKeyValue();
  }
}
