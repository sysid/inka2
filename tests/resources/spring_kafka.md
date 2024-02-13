# Spring Kafka .....................................................................................

<!--ID:1706289784923-->
1. Explain Spring Kafka annotations:
- provide a high-level abstraction for Kafka consumers, producers, and stream processors, simplifying the development of complex Kafka applications.
> 21. **`@EnableKafka`**: Enables Kafka listener annotated endpoints that are created under the cover by `@KafkaListener`. This annotation is typically used on `@Configuration` classes.
>       ```java
>       @Configuration
>       @EnableKafka
>       public class KafkaConfig {}
>       ```
>
> 22. **`@KafkaListener`**: Used on methods to create a listener endpoint. Such methods are invoked with data consumed from the specified Kafka topics.
>       ```java
>       @Service
>       public class KafkaConsumerService {
>           @KafkaListener(topics = "myTopic", groupId = "myGroup")
>           public void listen(String message) {
>               // process the message
>           }
>       }
>       ```
>
> 24. **`@SendTo`**: Used in conjunction with `@KafkaListener` to send the result of the listener method to the specified topic.
>       ```java
>       @Service
>       public class KafkaListenerService {
>           @KafkaListener(topics = "inputTopic")
>           @SendTo("outputTopic")
>           public String listenAndReply(String message) {
>               // process and return the response
>           }
>       }
>       ```
>
> 25. **`@TopicPartition`**: Used within `@KafkaListener` to define specific topic partitions to listen to.
>       ```java
>       @Service
>       public class KafkaConsumerService {
>           @KafkaListener(topicPartitions = @TopicPartition(topic = "myTopic", partitions = { "0", "1" }))
>           public void listenToPartition(String message) {
>               // process the message
>           }
>       }
>       ```
>
> 26. **`@PartitionOffset`**: Used with `@TopicPartition` to define a specific starting offset for a partition.
>       ```java
>       @Service
>       public class KafkaConsumerService {
>           @KafkaListener(topicPartitions = @TopicPartition(topic = "myTopic",
>               partitions = "0",
>               partitionOffsets = @PartitionOffset(partition = "0", initialOffset = "100")))
>           public void listenToPartitionFromOffset(String message) {
>               // process the message
>           }
>       }
>       ```
>
> 27. **`@KafkaHandler`**: Used in multi-method listeners to designate methods to handle records of different types.
>     - **Example**:
>       ```java
>       @Service
>       public class MultiMethodKafkaListenerService {
>           @KafkaListener(id = "multiMethods", topics = "myTopic")
>           public class MultiListener {
>               @KafkaHandler
>               public void listen(String message) {
>                   // handle String message
>               }
>
>               @KafkaHandler(isDefault = true)
>               public void listenDefault(Object message) {
>                   // default handler
>               }
>           }
>       }
>       ```

---

# Kafka Streams in Spring Boot  ...................................................................

---
1. Explain Spring Boot Kafka Streams:
> Kafka Streams is library for building applications, where input and output is stored in Kafka topics
> - don’t need to manually create an instance of a Kafka Streams object, start it and stop it, etc.
> - However, you can still get access to the object if you need it.
> - JSON serialization works out of the box.
>
> ## Configuration
> - simply add `@EnableKafkaStreams`, if you have Kafka Streams JARs in your classpath, they will be picked up by the autoconfiguration.
>
> - Autoconfiguration requires `KafkaStreamsConfiguration` bean with the name as specified by `DEFAULT_STREAMS_CONFIG_BEAN_NAME`.
> - configuration creates KafkaStreams client
> ```java
> @Configuration
> @EnableKafka
> @EnableKafkaStreams
> public class KafkaConfig {
>
>     @Value(value = "${spring.kafka.bootstrap-servers}")
>     private String bootstrapAddress;
>
>     @Bean(name = KafkaStreamsDefaultConfiguration.DEFAULT_STREAMS_CONFIG_BEAN_NAME)
>     KafkaStreamsConfiguration kStreamsConfig() {
>         Map<String, Object> props = new HashMap<>();
>         props.put(APPLICATION_ID_CONFIG, "streams-app");
>         props.put(BOOTSTRAP_SERVERS_CONFIG, bootstrapAddress);
>         props.put(DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
>         props.put(DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
>
>         return new KafkaStreamsConfiguration(props);
>     }
>
>     // other config
> }
> ```
>
> ## Processor topology
> - source node receives streaming data from Kafka, passes it to processor nodes, and flows out through the sink nodes to new Kafka topic.
> - edges represent the flow of the stream events
> - state of the stream is saved periodically using checkpoints for fault tolerance and resilience.
> - `StreamsBuilder` is required to build topology, provides access to all APIs available in Kafka Streams. It then becomes just a regular Kafka Streams application.
> ### DSL approach:
> ```java
> @Component
> public class WordCountProcessor {
>
>     private static final Serde<String> STRING_SERDE = Serdes.String();
>
>     @Autowired
>     void buildPipeline(StreamsBuilder streamsBuilder) {
>         KStream<String, String> messageStream = streamsBuilder
>           .stream("input-topic", Consumed.with(STRING_SERDE, STRING_SERDE));
>
>         KTable<String, Long> wordCounts = messageStream
>           .mapValues((ValueMapper<String, String>) String::toLowerCase)
>           .flatMapValues(value -> Arrays.asList(value.split("\\W+")))
>           .groupBy((key, word) -> word, Grouped.with(STRING_SERDE, STRING_SERDE))
>           .count();
>
>         wordCounts.toStream().to("output-topic");
>     }
> }
> ```
>
> ## Testing
> ### unit test
> - main test tool: `TopologyTestDriver`, eliminates the need to have a broker running and still verify the pipeline behavior
> - first thing required is the Topology that encapsulates our business logic under test
> ```java
> @Test
> void givenInputMessages_whenProcessed_thenWordCountIsProduced() {
>     StreamsBuilder streamsBuilder = new StreamsBuilder();
>     wordCountProcessor.buildPipeline(streamsBuilder);
>     Topology topology = streamsBuilder.build();
>
>     try (TopologyTestDriver topologyTestDriver = new TopologyTestDriver(topology, new Properties())) {
>         TestInputTopic<String, String> inputTopic = topologyTestDriver
>           .createInputTopic("input-topic", new StringSerializer(), new StringSerializer());
>
>         TestOutputTopic<String, Long> outputTopic = topologyTestDriver
>           .createOutputTopic("output-topic", new StringDeserializer(), new LongDeserializer());
>
>         inputTopic.pipeInput("key", "hello world");
>         inputTopic.pipeInput("key2", "hello");
>
>         assertThat(outputTopic.readKeyValuesToList())
>           .containsExactly(
>             KeyValue.pair("hello", 1L),
>             KeyValue.pair("world", 1L),
>             KeyValue.pair("hello", 2L)
>           );
>     }
> }
> ```

---



## Monitoring
to monitor: Kafka Streams exposes some methods through JMX, and Spring Kafka provides a wrapper around those metrics and makes them available through the Micrometer framework.
This allows you to consume the metrics with other frameworks and dashboard tools. In addition, Spring provides some out-of-the-box implementations for error handling.


# Resources ........................................................................................
## Tutorial
[Kafka Streams With Spring Boot](https://www.baeldung.com/spring-boot-kafka-streams)
Associated Repo: /Users/Q187392/dev/s/forked/tutorials/spring-kafka/src/main/java/com/baeldung/kafka/streams

