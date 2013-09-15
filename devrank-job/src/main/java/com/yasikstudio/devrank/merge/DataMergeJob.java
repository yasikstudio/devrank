package com.yasikstudio.devrank.merge;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.PosixParser;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.Tool;

public class DataMergeJob implements Tool {

  private Configuration configuration;

  @Override
  public int run(String[] args) throws Exception {
    Options options = new Options();
    options.addOption("h", "help", false, "Help");
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

    String inputPath = cmd.getOptionValue("inputPath");
    String outputPath = cmd.getOptionValue("outputPath");

    String jobname = "devrank-job-merge-" + System.currentTimeMillis();
    Job job = new Job(getConf(), jobname);
    job.setJarByClass(DataMergeJob.class);

    job.setMapperClass(DataMergeMapper.class);
    job.setCombinerClass(DataMergeCombiner.class);
    job.setReducerClass(DataMergeReducer.class);

    job.setMapOutputKeyClass(Text.class);
    job.setMapOutputValueClass(UserRecord.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(NullWritable.class);

    FileInputFormat.addInputPath(job, new Path(inputPath));
    FileOutputFormat.setOutputPath(job, new Path(outputPath));

    return job.waitForCompletion(true) ? 0 : 1;
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
