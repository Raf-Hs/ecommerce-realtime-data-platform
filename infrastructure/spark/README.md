# Spark Infrastructure

## Requirements

- Java 17+ (JDK). Spark 4.x requires Java 17 or later.
- Python 3.10+ with `pyspark` and `delta-spark` installed (see `requirements.txt`).

## Install Java (WSL/Ubuntu, no sudo)

```bash
mkdir -p ~/jdk && cd ~/jdk
wget https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.13%2B11/OpenJDK17U-jdk_x64_linux_hotspot_17.0.13_11.tar.gz -O jdk17.tar.gz
tar -xzf jdk17.tar.gz
export JAVA_HOME=~/jdk/jdk-17.0.13+11
export PATH=$JAVA_HOME/bin:$PATH
```

Persist `JAVA_HOME` in `~/.bashrc`.

## Run the streaming job

```bash
export JAVA_HOME=~/jdk/jdk-17.0.13+11
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0,io.delta:delta-spark_4.2_2.13:4.4.1 \
    src/streaming/spark_streaming.py
```

## Smoke test

```bash
JAVA_HOME=~/jdk/jdk-17.0.13+11 python scripts/spark_smoke_test.py
```