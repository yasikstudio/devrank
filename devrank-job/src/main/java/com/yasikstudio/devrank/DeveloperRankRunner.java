package com.yasikstudio.devrank;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.PosixParser;
import org.apache.giraph.graph.GiraphJob;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.Tool;

public class DeveloperRankRunner implements Tool {

  private Configuration configuration;

  @Override
  public int run(String[] args) throws Exception {
    Options options = new Options();
    options.addOption("h", "help", false, "Help");
    options.addOption("w", "workers", true, "Number of workers");
    options.addOption("i", "inputPath", true, "Input Path");
    options.addOption("o", "outputPath", true, "Output Path");

    HelpFormatter formatter = new HelpFormatter();
    if (args.length == 0) {
      formatter.printHelp(getClass().getName(), options, true);
      return 0;
    }
    CommandLineParser parser = new PosixParser();
    CommandLine cmd = parser.parse(options, args);
    if (cmd.hasOption('h')) {
      formatter.printHelp(getClass().getName(), options, true);
      return 0;
    }

    int workers = Integer.parseInt(cmd.getOptionValue('w'));

    GiraphJob job = new GiraphJob(getConf(), getClass().getName());
    job.setVertexClass(DeveloperRankVertex.class);
    job.setVertexInputFormatClass(DeveloperRankVertexInputFormat.class);
    job.setVertexOutputFormatClass(DeveloperRankVertexOutputFormat.class);
    FileInputFormat.addInputPath(job,
      new Path(cmd.getOptionValue("inputPath")));
    FileOutputFormat.setOutputPath(job,
      new Path(cmd.getOptionValue("outputPath")));

    job.setWorkerConfiguration(workers, workers, 100.0f);
    return job.run(true) ? 0 : -1;
  }

  @Override
  public Configuration getConf() {
    return configuration;
  }

  @Override
  public void setConf(Configuration configuration) {
    this.configuration = configuration;
  }
}
