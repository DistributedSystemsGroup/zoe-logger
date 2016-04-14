# zoe-logger
Optional [Zoe](http://zoe-analytics.eu) process to translate Docker GELF logs into Kafka.

This simple daemon reads log messages produced by Docker in GELF format, extracts some Zoe-related labels and sends the output to Kafka.

The output is composed of one syslog-like line per log message containing most of the useful information available in the GELF message.

The output produced by containers in a Swarm cluster is difficult to manage at scale. On one side you need to save the output for auditing and analysis, on the other you want to have real-time access to the output of your processes, most often of a single container when there is a problem to debug.

Kafka provides a nice way to cater for both needs, but unfortunately Docker [does not support Kafka directly](https://github.com/docker/docker/issues/21271) as a log destination. This is why this daemon was born.

 ## Configuration

Create a configuration file named `zoe-logger.py` in the same directory as `zoe-logger.py`, or in `/etc/zoe/`.

Options can be passed also via command-line or environment variables.

The options are:
* `debug`: enable debug output
* `kafka-broker`: address of the Kafka broker

Zoe-logger will listen for incoming messages on UDP port 12201.

## Dockerfile

Zoe-logger can be run with Docker itself.

You can use the `ZOE_LOGGER_KAFKA_BROKER` environment variable to pass the Kafka address to the Zoe logger.

 ```
 docker run -d -p 12201:12201/udp -e ZOE_LOGGER_KAFKA_BROKER=localhost:9092 --restart=always zoerepo/zoe-logger
 ```

## Reading logs

The `showlog.py` script can be used to look at logs stored in Kafka. Each container logs to its own topic. The script is able to list all topics and do the equivalent of `tail -f` on a specific topic.

Use `showlog.py --help` for more details.
