package com.yasikstudio.devrank.util;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStreamReader;

public class ESLauncher {
  private static final String USAGE =
      "Usage: java jar esclient-xxx-with-dependencies.jar [hostname] [filename]";

  public static void main(String[] args) throws Exception {
    if (args.length != 2) {
      usageWithExit();
    }
    ESClient es = new ESClient(args[0]);
    BufferedReader r =
        new BufferedReader(new InputStreamReader(new FileInputStream(args[1])));
    updateRanks(es, r);
    r.close();
  }

  private static void updateRanks(ESClient es, BufferedReader r)
      throws Exception {
    String line = null;
    while ((line = r.readLine()) != null) {
      String[] data = line.split(",");
      String uid = data[0];
      double folValue = Double.parseDouble(data[1]);
      double actValue = Double.parseDouble(data[2]);
      double v = folValue + actValue;
      System.out.print(String.format("%s : %.30f => ", uid, v));
      String result = null;
      int retry = 20;
      while (retry > 0) {
        try {
          result = es.update(uid, v);
        } catch (Exception e) {
          if (retry <= 0) {
            throw e;
          } else {
            try {
              Thread.sleep(100);
            } catch (Throwable t) {
            }
          }
        }
        retry--;
      }
      System.out.println(result);
    }
  }

  private static void usageWithExit() {
    System.out.println(USAGE);
    System.exit(-1);
  }
}
