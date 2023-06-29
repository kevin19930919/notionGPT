# Part II. Distributed Data

## Reasons why you might want to distribute a database across multiple machines

- *Scalability*
- *Fault tolerance/high availability*
- *Latency (users around the world)*

## **Scaling to Higher Load**

### *shared-memory architecture*

buy a more powerful machine

- cost grows faster than linearly.
- a machine twice the size cannot necessarily handle twice the load.
- but it is definitely limited to a single geographic location

### *shared-disk architecture*

locking limit the scalability of the shared-disk approach

### *shared-nothing architectures (We focus on)*

it usually also incurs additional complexity for applications and sometimes limits the expressiveness of the data models you can use.

**

## **Replication Versus Partitioning**

### *Replication*

Keeping a copy of the same data on several different nodes

### *Partitioning*

Splitting a big database into smaller subsets

## Partition vs Sharding

### Partitioning:

It is a technique of dividing a large database into smaller, more manageable parts called partitions, based on certain rules. These rules can be based on different criteria such as a range of values (like dates), a list of values, or a hash function. 

The data within each partition is physically stored together and can be accessed quickly. This method helps in improving query performance by allowing operations to run in parallel on different partitions.

1. **Horizontal Partitioning**: This type of partitioning, also known as "row partitioning," involves dividing a database into two or more tables, each containing different rows of the original table. Each partition forms a subset of data. Sharding is a type of horizontal partitioning where different rows (records) are stored on different servers.
2. **Vertical Partitioning:** In this type of partitioning, also referred to as "column partitioning," the database is divided into two or more tables that contain different columns of the original table. This technique is useful when certain columns of the table are accessed together more frequently than others. It helps reduce disk I/O and can improve query performance.

### Sharding:

Sharding is a method of splitting and storing **a single logical dataset in multiple databases**. Each part is referred to as a shard and can be placed on a different server, reducing the load on each one. It's a way of horizontally partitioning data; each shard holds a different set of data but with the same schema.

 Sharding helps in distributing the load, thus improving performance and allowing the database to scale horizontally.

You can take sharding as a specific form of horizontal partitioning, but spread across multiple servers or databases