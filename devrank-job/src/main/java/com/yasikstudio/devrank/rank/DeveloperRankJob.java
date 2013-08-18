package com.yasikstudio.devrank.rank;

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
    options.addOption("e", "elasticSearch", true, "address of ElasticSearch "
        + "(ex: http://localhost:9200");

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
    String esAddress = cmd.getOptionValue("elasticSearch");

    configuration.setLong("superstep", supersteps);
    configuration.set("elasticSearch", esAddress);

    GiraphJob job = new GiraphJob(getConf(), "devrank-job-rank");
    job.setVertexClass(DeveloperRankVertex.class);
    job.setVertexInputFormatClass(DeveloperRankVertexInputFormat.class);
    job.setVertexOutputFormatClass(DeveloperRankVertexOutputFormat.class);
    FileInputFormat.addInputPath(job, new Path(inputPath));
    FileOutputFormat.setOutputPath(job, new Path(outputPath));

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
