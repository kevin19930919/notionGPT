# Chapter 4. Encoding and Evolution

## Summary

# Formats for encoding data

Two different representations:

- In memory
- When you want to write data to a file or send it over the network, you have to encode it

> A translation between the two representations. **In-memory** representation to **byte sequence** is called *encoding* (*serialisation* or *marshalling*), and the reverse is called *decoding* (*parsing*, *deserialisation* or *unmarshalling*).
> 

Programming languages come with built-in support for encoding in-memory objects into byte sequences, but is usually a bad idea to use them. 許多程式語言都內建了將記憶體物件編碼為位元組序列的支援。例如，Java 有 `java.io.Serializable`
【1】，Ruby 有 `Marshal`
【2】，Python 有 `pickle`
【3】，等等。許多第三方庫也存在，例如 `Kryo for Java`
【4】。Precisely because of a few problems.

- Often tied to a particular programming language.
- The decoding process needs to be able to instantiate arbitrary classes and this is frequently a security hole(ex: An attacker can inject the first constructor argument).
- Versioning
- Efficiency

[JSON, XML, and CSV](https://digitalhospital.com.sg/csv-vs-xml-vs-json-which-is-the-best-response-data-format/) are human-readable and popular specially as data interchange formats, but they have some subtle problems:

- Ambiguity around the encoding of numbers and dealing with large numbers
- Support of Unicode character strings, but no support for binary strings. People get around this by encoding binary data as Base64, which increases the data size by 33%.
- There is optional schema support for both XML and JSON
- CSV does not have any schema

### **Binary encoding**

Applications inevitably change over time. Features are added or modified as new products are launched, user requirements become better understood, or business circumstances change. In [Chapter 1](https://github.com/Vonng/ddia/blob/master/en-us/ch1.mdj) we introduced the idea of *evolvability*: we should aim to build systems that make it easy to adapt to change (see “[Evolvability: Making Change Easy](https://github.com/Vonng/ddia/blob/master/en-us/ch1.md#evolvability-making-change-easy)”).

In most cases, a change to an application’s features also requires a change to data that it stores: perhaps a new field or record type needs to be captured, or perhaps existing data needs to be presented in a new way.

The data models we discussed in [Chapter 2](https://github.com/Vonng/ddia/blob/master/en-us/ch2.md) have different ways of coping with such change. Relational databases generally assume that all data in the database conforms to one schema: although that schema can be changed (through schema migrations; i.e., ALTER statements), there is exactly one schema in force at any one point in time. By contrast, schema-on-read (“schemaless”) databases don’t enforce a schema, so the database can contain a mixture of older and newer data formats written at different times (see “[Schema flexibility in the document model](https://github.com/Vonng/ddia/blob/master/en-us/ch3.md#schema-flexibility-in-the-document-model)”).

When a data format or schema changes, a corresponding change to application code often needs to happen (for example, you add a new field to a record, and the application code starts reading and writing that field). However, in a large application, code changes often cannot happen instantaneously:

- With server-side applications you may want to perform a *rolling upgrade* (also known as a *staged rollout*), deploying the new version to a few nodes at a time, checking whether the new version is running smoothly, and gradually working your way through all the nodes. This allows new versions to be deployed without service downtime, and thus encourages more frequent releases and better evolvability.
- With client-side applications you’re at the mercy of the user, who may not install the update for some time.

This means that old and new versions of the code, and old and new data formats, may potentially all coexist in the system at the same time. In order for the system to continue running smoothly, we need to maintain compatibility in both directions:

***Backward compatibility***

Newer code can read data that was written by older code.

***Forward compatibility***

Older code can read data that was written by newer code.

Backward compatibility is normally not hard to achieve: as author of the newer code, you know the format of data written by older code, and so you can explicitly handle it (if necessary by simply keeping the old code to read the old data). Forward compatibility can be trickier, because it requires older code to ignore additions made by a newer version of the code.

In this chapter we will look at several formats for encoding data, including JSON, XML, Protocol Buffers, Thrift, and Avro. In particular, we will look at how they handle schema changes and how they support systems where old and new data and code need to coexist. We will then discuss how those formats are used for data storage and for communication: in web services, Representational State Transfer (REST), and remote procedure calls (RPC), as well as message-passing systems such as actors and message queues.

JSON is less verbose than XML, but both still use a lot of space compared to binary formats. There are binary encodings for JSON (MesagePack, BSON, BJSON, UBJSON, BISON and Smile), similar thing for XML (WBXML and Fast Infoset).

**Apache Thrift and Protocol Buffers (protobuf) are binary encoding libraries.**

![Screen Shot 2023-05-23 at 12.17.42 PM.png](Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa/Screen_Shot_2023-05-23_at_12.17.42_PM.png)

![Screen Shot 2023-05-23 at 12.15.38 PM.png](Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa/Screen_Shot_2023-05-23_at_12.15.38_PM.png)

Thrift offers two different protocols:

- **BinaryProtocol**, there are no field names like `userName`, `favouriteNumber`. Instead the data contains *field tags*, which are numbers (`1`, `2`)
- **CompactProtocol**, which is equivalent to BinaryProtocol but it packs the same information in less space. It packs the field type and the tag number into the same byte.

Protocol Buffers are very similar to Thrift's CompactProtocol, bit packing is a bit different and that might allow smaller compression.

Schemas inevitable need to change over time (*schema evolution*), how do Thrift and Protocol Buffers handle schema changes while keeping backward and forward compatibility changes?

- **Forward compatible support**. As with new fields you add new tag numbers, old code trying to read new code, it can simply ignore not recognised tags.
- **Backwards compatible support**. As long as each field has a unique tag number, new code can always read old data. Every field you add after initial deployment of schema must be optional or have a default value.

The only detail is that **if you add a new field, you cannot make it required**.
If you were to add a field and make it required, that check would fail if new code read
data written by old code, because the old code will not have written the new field that
you added. Therefore, to maintain backward compatibility, every field you add after
the initial deployment of the schema must be optional or have a default value.

Removing fields is just like adding a field with backward and forward concerns reversed. You can only remove a field that is optional, and you can never use the same tag again.

What about changing the data type of a field? There is a risk that values will lose precision or get truncated.

## Avro

Apache Avro is another binary format that has **two schema languages**, one intended for human editing (Avro IDL), and one (based on JSON) that is more easily machine-readable.

```sql
// Avro IDL
record Person {
    string                userName;
    union { null, long }  favoriteNumber = null;
    array<string>         interests;
}
```

```json
// Json
{
  "type": "record",
  "name": "Person",
  "fields": [
    { "name": "userName", "type": "string" },
    { "name": "favoriteNumber", "type": ["null", "long"], "default": null },
    { "name": "interests", "type": { "type": "array", "items": "string" } }
  ]
}
```

You go through the fields in the order they appear in the **schema** and use the schema to tell you the datatype of each field. **Any mismatch in the schema between the reader and the writer would mean incorrectly decoded data.**

![Screen Shot 2023-05-22 at 10.07.33 PM.png](Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa/Screen_Shot_2023-05-22_at_10.07.33_PM.png)

**There is nothing identifying the field or its data type.** Encodings simply consist of values concatenated together. A string is just a length prefix followed by UTF-8 bytes, but there's nothing in the included data to tell you it's a string. It can be an integer or other integers. Integers are encoded using variable length encoding (the same as Thrift's CompactProtocol).

### Schema evolution

- When an application wants to encode some data, it encodes the data using whatever version of the schema it knows (***writer's schema***).
- When an application wants to decode some data, it is expecting the data to be in some schema (***reader's schema***).

In Avro the writer's schema and the reader's schema *don't have to be the same*. The Avro library resolves the differences by looking at the writer's schema and the reader's schema.

- Forward compatibility means you can have a new version of the schema as writer and an old version of the schema as reader.
- Backward compatibility means that you can have a new version of the schema as reader and an old version as writer.

To maintain compatibility, you may only add or remove a field that has a default value.

If you were to add a field that has no default value, new readers wouldn't be able to read data written by old writers.

1. Use field names for matching. Therefore, it does not matter if the order of the field names in the write mode and the read mode are different.
2. Extra fields are ignored.
3. Fill in default values for missing fields.

Changing the datatype of a field is possible, provided that Avro can convert the type. Changing the name of a filed is tricky (backward compatible but not forward compatible).

### How to get write mode from encoding

1. A large file with the same structure of all data entries is typical in the Hadoop ecosystem. If all records in a large file are encoded with the same mode, it is sufficient to include the write-once mode in the file header.
2. Database Tables That Support Schema Changes Because database tables allow schema modifications, rows within them may be written in different schema phases. For this case, you can additionally record a schema version number (such as auto-increment) when coding, and then store all schema versions somewhere. When decoding, just query the corresponding writing mode through the version.
3. Sending data over the network During the handshake phase of communication between two processes, the write mode is exchanged. For example, exchange modes at the beginning of a session, and then use this mode throughout the session life cycle.

### Code Generation and Dynamic Languages

Avro, compared to Protocol Buffers and Thrift, has the advantage of **not including any tag numbers in its schemas**. This is important because it simplifies schema evolution. In Avro, schemas can be dynamically generated, making it ideal for scenarios like dumping the contents of a relational database into a file in a binary format. Avro can easily create schemas from the relational schema, encode the database content, and dump it all into an Avro object container file. If the database schema changes, a new Avro schema can be generated from the updated database schema, and the data can be exported without any special attention to the schema changes.

Code generation is heavily relied upon in Thrift and Protobuf, which is beneficial in statically typed languages such as Java, C++, or C#, as it allows for efficient in-memory data structures for the decoded data and for type checks and auto-completion during coding. 

However, in dynamically typed languages like JavaScript, Ruby, or Python, code generation doesn't make much sense because there are no compile-time type checkers to satisfy.

Avro, on the other hand, provides optional code-generation capabilities for statically typed languages, but it can also be used without generating any code. If you have an object container file, you can simply open it using the Avro library and view the data as if viewing a JSON file. This feature is especially useful for dynamically typed data processing languages like Apache Pig, allowing you to analyze and output Avro files without considering schemas.

---

Although textual formats such as JSON, XML and CSV are widespread, binary encodings based on schemas are also a viable option. As they have nice properties:

- Can be much more compact, since they can omit field names from the encoded data.
- Schema is a valuable form of documentation, required for decoding, you can be sure it is up to date.
- Database of schemas allows you to check forward and backward compatibility changes.
- Generate code from the schema is useful, since it enables type checking at compile time.

# Type of dataflow

1. Through a Database: One process writes data into the database, and another process reads this data. 
2. Through Service Calls: This method involves one process making a request to another process, which in turn responds with the requested data. This is often used in a client-server architecture where the client makes requests to the server for data. 
3. Through Asynchronous Message Passing: This method is often used in distributed systems where processes run independently and communicate by sending and receiving messages. Messages can be sent to a queue or a message broker and then read by the recipient when they are ready. 

## Through Database

Typically, multiple different processes concurrently accessing the database are common. These processes may be different applications or services. Some of the processes accessing the database might be running newer code while others might be running older code, for instance, because a new version is currently being deployed in a rolling upgrade.

There is an edge case. If you add a field to a record schema, and the newer code writes a value for that new field to the database, then the old code reads the record, updates it, and writes it back. In this situation, the ideal behavior is usually for the old code to leave the new field untouched, even though it can't interpret it.

![Screen Shot 2023-05-22 at 11.58.51 PM.png](Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa/Screen_Shot_2023-05-22_at_11.58.51_PM.png)

### Data Written at Different Times

For applications, an older version can be replaced by a new one in a relatively short time. However, for data, the amount written by older versions of the code can be substantial over time. After changing the schema, the cost of updating all this old schema data to align with the new version can be high due to the large volume of old schema data.

Upon reading, databases generally handle old data that lacks corresponding columns by:

1. Filling in default values for the new version fields (default value)
2. If there are no default values, then filling in null values (nullable)

Then, this data is returned to the user. Generally speaking, when changing schemas (such as with an alter table), databases do not allow the addition of columns that neither have default values nor allow null values.

## Through Service Calls

When we need inter process communication, the most common way involves  client and server. The server exposes an API over the network, and the client can connect to the server to make requests to that API. The API that the server exposes is known as a service.

The Web operates in this manner: clients (Web browsers) make requests to web servers, fetching HTML, CSS, JavaScript, images, etc., via GET requests and submitting data to the server via POST requests. The API consists of a set of standard protocols and data formats (HTTP, URLs, SSL/TLS, HTML, etc.).

Furthermore, servers can themselves be clients of another service (for example, a typical web application server acts as a client to a database). This approach is typically used to break down large applications into smaller services by functionality, where one service makes a request to another when it needs some functionality or data from it. This way of building applications has traditionally been known as a service-oriented architecture (SOA) and has recently been refined and rebranded as a microservice architecture.

### Web service

When a service uses HTTP as its underlying communication protocol, it can be referred to as a Web service

1. Client applications running on user devices make requests to services via HTTP. These requests typically go through the public internet.
2. One service makes requests to another service owned by the same organization, typically located within the same data center, as part of a service-oriented/microservices architecture. 
3. One service makes requests to a service owned by a different organization over the internet. This is used for data exchange between backend systems of different organizations. 

There are two main approaches to designing HTTP APIs: REST and SOAP.

1. REST is not a protocol, but rather a design philosophy. It emphasizes simple API formats, using URLs to identify resources, and uses HTTP actions (GET, POST, PUT, DELETE) to perform CRUD operations on the resources. Because of its simple style, it is becoming increasingly popular.
2. SOAP is an XML-based protocol. Although it uses HTTP, its goal is to be independent of HTTP. It's mentioned less often these days.

![Screen Shot 2023-05-23 at 9.32.32 AM.png](Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa/Screen_Shot_2023-05-23_at_9.32.32_AM.png)

### Remote procedure call (RPC)

RPC tries to make calling remote services as natural as calling local (in-process) functions. Although the idea is good and it is used quite a lot now, there are some problems:

1. Local function calls either succeed or fail. But because RPC goes through the network, there may be various complex situations, such as request loss, response loss, hanging leading to timeouts, etc. Therefore, retries may be needed.
2. If retrying, idempotency needs to be considered. Because the last request might have already reached the server, only the request did not successfully return. So multiple calls to remote functions must ensure that they do not cause additional side effects.
3. Remote call latency is unpredictable and heavily influenced by the network.
4. The programming languages used by the client and server may be different, but if there are some types that are not shared by both, there will be some problems.

![Screen Shot 2023-05-23 at 9.33.33 AM.png](Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa/Screen_Shot_2023-05-23_at_9.33.33_AM.png)

Even though the issues mentioned exist, in engineering, most of the time, these conditions are within the tolerance range

Additionally, RPC based on binary encoding is generally more efficient than HTTP services. But the benefit of HTTP services, or more specifically, RESTful APIs, is the rich ecosystem and extensive tooling support. On the other hand, the APIs of RPC are usually highly related to the code generated by the RPC framework, making it difficult to interchange and upgrade seamlessly across different organizations.

- **REST** is often used for public API.
- **RPC** is often used for internal communication in microservices architecture, where the added flexibility and potential for performance optimization can be beneficial.

Data flow through services usually assumes that all servers are updated first, followed by the clients. Therefore, backward compatibility needs to be considered in requests, and forward compatibility in responses:

- Thrift, gRPC (Protobuf), and Avro RPC can evolve according to the compatibility rules of the encoding format.
- RESTful APIs typically use JSON as the request and response format, which makes it easy to add new fields for evolution and compatibility.
- SOAP looks suck
- Thrift, gRPC (Protobuf), and Avro RPC can evolve according to the compatibility rules of the encoding format.
- RESTful APIs typically use JSON as the request and response format, which makes it easy to add new fields for evolution and compatibility.
- SOAP is not discussed here.
- Thrift, gRPC (Protobuf), and Avro RPC can evolve according to the compatibility rules of the encoding format.
- RESTful APIs typically use JSON as the request and response format, which makes it easy to add new fields for evolution and compatibility.
- SOAP is not discussed here.

There's no consensus on how API versioning should work (i.e., how a client indicates which version of the API it wants to use). For RESTful APIs, common methods include using the version number in the URL or the HTTP Accept header. For services that use API keys to identify specific clients, another option is to store the API version requested by the client on the server, and allow that version option to be updated through a separate management interface.

## Message broker

![0_ubsIB5P8egtyni9g.png](Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa/0_ubsIB5P8egtyni9g.png)

- Message-passing communication is usually one-way.
- This communication pattern is *asynchronous*: the sender doesn’t wait for the message to be delivered, but simply sends it and then forgets about it.

### Pros

- It can act as a buffer if the recipient is unavailable or overloaded, and thus
improve system reliability.
- It can automatically redeliver messages to a process that has crashed, and thus
prevent messages from being lost.
- It avoids the sender needing to know the IP address and port number of the
recipient (which is particularly useful in a cloud deployment where virtual
machines often come and go).
- It allows one message to be sent to several recipients.
- It logically decouples the sender from the recipient (the sender just publishes
messages and doesn’t care who consumes them).

### **Distributed actor frameworks**

The *actor model* is a programming model for concurrency in a single process.

A distributed actor framework essentially integrates a message broker and the actor programming model into a single framework

# Summary

During rolling upgrades, or for various other reasons, we must assume that different nodes are running the different versions of our application’s code. Thus, it is important that all data flowing around the system is encoded in a way that provides back‐ward compatibility (new code can read old data) and forward compatibility (old code can read new data).

### Data encoding formats

- Programming language–specific encodings are restricted to a single program‐
ming language and often fail to provide forward and backward compatibility.
- JSON, XML, and CSV are widespread. These formats are somewhat vague about datatypes, so you have to be careful with things like numbers and binary strings.
- Binary schema–driven formats like Thrift, Protocol Buffers, and Avro allow compact, efficient encoding with clearly defined forward and backward compati‐ bility semantics.

### Modes of dataflow which data encodings are important

- Databases
- RPC and REST APIs
- Asynchronous