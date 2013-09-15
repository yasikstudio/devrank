package com.yasikstudio.devrank.rank;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.PosixParser;
import org.apache.giraph.conf.GiraphConfiguration;
import org.apache.giraph.io.formats.GiraphFileInputFormat;
import org.apache.giraph.job.GiraphJob;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.Tool;

public class DeveloperRankJob implements Tool {

  private Configuration configuration;

  @Override
  public int run(String[] args) throws Exception {
    Options options = new Options();
    options.addOption("h", "help", false, "Help");
    options.addOption("i", "inputPath", true, "Input Path");
    options.addOption("o", "outputPath", true, "Output Path");
    options.addOption("w", "workers", true, "Number of workers");
    options.addOption("s", "supersteps", true, "Number of supersteps");

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

    int workers = Integer.parseInt(cmd.getOptionValue('w', "1"));
    long supersteps = Long.parseLong(cmd.getOptionValue('s', "10"));
    String inputPath = cmd.getOptionValue("inputPath");
    String outputPath = cmd.getOptionValue("outputPath");

    configuration.setLong("superstep", supersteps);

    String jobname = "devrank-job-rank-" + System.currentTimeMillis();
    GiraphJob job = new GiraphJob(getConf(), jobname);
    GiraphConfiguration giraphConf = job.getConfiguration();
    giraphConf.setVertexClass(DeveloperRankVertex.class);
    giraphConf.setVertexInputFormatClass(DeveloperRankVertexInputFormat.class);
    giraphConf.setVertexOutputFormatClass(DeveloperRankVertexOutputFormat.class);
    GiraphFileInputFormat.addVertexInputPath(job.getConfiguration(), new Path(inputPath));
    FileOutputFormat.setOutputPath(job.getInternalJob(), new Path(outputPath));
    giraphConf.setWorkerConfiguration(workers, workers, 100.0f);
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
