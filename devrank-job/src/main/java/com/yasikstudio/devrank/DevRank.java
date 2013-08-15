package com.yasikstudio.devrank;

import java.util.HashMap;
import java.util.Map;

import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

import com.google.common.base.Joiner;
import com.yasikstudio.devrank.merge.DataMergeJob;
import com.yasikstudio.devrank.rank.DeveloperRankJob;

public class DevRank {
  private static Map<String, Class<?>> jobs = new HashMap<String, Class<?>>();

  static {
    jobs.put("rank", DeveloperRankJob.class);
    jobs.put("merge", DataMergeJob.class);
  }

  public static void main(String[] args) throws Exception {
    if (args.length == 0) {
      usageWithExit();
    }

    String cmd = args[0];
    if (!jobs.containsKey(cmd)) {
      usageWithExit();
    }

    int length = args.length - 1;
    String[] arguments = new String[length];
    System.arraycopy(args, 1, arguments, 0, length);

    Tool job = (Tool) jobs.get(cmd).newInstance();
    System.exit(ToolRunner.run(job, arguments));
  }

  private static void usageWithExit() {
    String jarname = "devrank-x.x.x-jar-with-dependencies.jar";
    String joblist = Joiner.on("|").join(jobs.keySet());
    System.out.printf("Usage: hadoop jar %s [%s]\n", jarname, joblist);
    System.exit(-1);
  }
}
