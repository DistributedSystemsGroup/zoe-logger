# Docker logger
This repository contains a pipeline to recover logs generated by Docker containers, write them to Kafka and then consume them for long term storage into Postgresql.

The consumer can be easily changed or rewritten to store logs somewhere else.

The output produced by containers in a Swarm cluster is difficult to manage at scale. On one side you need to save the output for auditing and analysis, on the other you want to have real-time access to the output of your processes, most often of a single container when there is a problem to debug.

Unfortunately Docker [does not support Kafka directly](https://github.com/docker/docker/issues/21271) as a log destination. This is why the producer part of this repository was born.

## Configuration

### Producer

The zoe-logger process listens for UDP packets generated by Docker containing logs in GELF format.

You need to configure your docker engines (or use the `docker run` command line switches), for example: `--log-driver=gelf --log-opt gelf-address=udp://192.168.45.25:12201`

Create a configuration file named `zoe-logger.py` in the same directory as `zoe-logger.py`, or in `/etc/zoe/`.

Options can be passed also via command-line or environment variables.

The options are:
* `debug`: enable debug output
* `kafka-broker`: address of the Kafka broker

Zoe-logger will listen for incoming messages on UDP port 12201.

We run the producer in a Docker container. Build it with:

### Consumer

The Consumer process is called `pq_consumer` and needs configuration about how to connect to the database.

The options are:
* `debug`: enable debug output
* `kafka-broker`: address of the Kafka broker
* `db_host`: DB host name
* `db_port`: DB port
* `db_name`: Database name (a table called logs will be created automatically)
* `db_user`: DB username
* `db_pass`: DB password

## Dockerfile

To build the image (an autobuilt image is available from the Docker Hub):
`docker build -t docker-logger .`

Zoe-logger can be run with Docker itself.

You can use the `ZOE_LOGGER_KAFKA-BROKER` environment variable to pass the Kafka address to the Zoe logger.

 ```
 docker run -d -p 12201:12201/udp -e ZOE_LOGGER_KAFKA-BROKER=localhost:9092 --restart=always zoerepo/zoe-logger
 ```

