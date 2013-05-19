package com.yasikstudio.devrank;

import org.apache.hadoop.util.ToolRunner;

public class DeveloperRank {
  public static void main(String[] args) throws Exception {
    System.exit(ToolRunner.run(new DeveloperRankRunner(), args));
  }
}
