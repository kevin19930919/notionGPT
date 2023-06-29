# Chapter 3. Storage and Retrieval

- Shows how databases handle storage and retrieval, i.e. store data and query data

## Data Structures That Power Your Database → index

- index is …
    - A signpost that helps you locate your data
    - An additional structure that is derived from your data
    - If well chosen will speed up query, but slows down writes

### Hash index

- key-value store, hash maps (hash index used in-memory)
- well suited for situation where the value are updated frequently
- Compaction: throws away duplicate key
    - Append only and segmentation files
    
    ![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled.png)
    
- Issues for real implementation
    - File format
    - Deleting records
    - Crash recovery
    - Partially written records
    - Concurrency control
- Pro and cons of hash index
    
    
    | Pros | Cons |
    | --- | --- |
    | Performant (compare to random read/write) | Must fit in memory |
    | Append-only makes concurrency and crash recovery simpler  | Range queries are not efficient |
    | Merging old segment avoids data get fragmented over time |  |

### SSTables and LSM-Tree

- Sorted String Table (SSTable): Sequence of key-value pairs sorted by key

### B tree index

[database_indexing.pptx](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/database_indexing.pptx)

### Compare LSM-Tree with B tree index

![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%201.png)

| Feature | LSM-tree (append only) | B-tree |
| --- | --- | --- |
| Data structure | Log-structured merge tree | Balanced tree |
| Write performance | Very fast | Slow |
| Read performance | Slow | Fast |
| Space efficiency | Good | Bad |
| Durability | High | Low |
| Scalability | Very good | Good |

Advantages of LSM-trees:

- LSM-trees are typically able to sustain higher write throughput than B-trees, party because they sometimes have **lower write amplification**: a write to the database results in multiple writes to disk. The more a storage engine writes to disk, the fewer writes per second it can handle.
- LSM-trees can be **compressed better**, and thus often produce smaller files on disk than B-trees. B-trees tend to leave disk space unused due to fragmentation.

Downsides of LSM-trees:

- Compaction process can sometimes interfere with the performance of ongoing reads and writes. B-trees can be more predictable. The bigger the database, the the more disk bandwidth is required for compaction. Compaction cannot keep up with the rate of incoming writes, if not configured properly you can run out of disk space.
- On B-trees, **each key exists in exactly one place in the index**. This offers strong transactional semantics. Transaction isolation is implemented using locks on ranges of keys, and in a B-tree index, those locks can be directly attached to the tree.

### Other **indexing structures**

- Secondary Index (not-unique)
- Storing values within the index
    - The key in an index is the thing that queries search for, but the value can be one of
    two things: it could be the actual row (document, vertex) in question, or it could be a
    reference to the row stored elsewhere. In the latter case, the place where rows are
    stored is known as a *heap file*,
    - Stores data in no particular order (it may be append-only, or it may keep track of deleted rows in order to overwrite them with new data later).
- Multi-column indexes
    - The most common type of multi-column index is called a *concatenated index*, which
    simply combines several fields into one key by appending one column to another (the
    index definition specifies in which order the fields are concatenated).
    - **Multi-dimensional index**
        
        ```sql
        **SELECT** * **FROM** restaurants **WHERE** latitude > 51.4946 **AND** latitude < 51.5079
        **AND** longitude > -0.1162 **AND** longitude < -0.1004;
        ```
        
    - A standard B-tree or LSM-tree index is not able to answer that kind of query effi‐
    ciently: it can give you either all the restaurants in a range of latitudes (but at any lon‐
    gitude), or all the restaurants in a range of longitudes (but anywhere between the
    North and South poles), but not both simultaneously.
- Full-text search and fuzzy indexes
    - Indexes don't allow you to search for *similar* keys, such as misspelled words. Such *fuzzy* querying requires different techniques.
    - Full-text search engines allow synonyms, grammatical variations, occurrences of words near each other.
    - Lucene uses SSTable-like structure for its term dictionary. Lucene, the in-memory index is a finite state automaton, similar to a *trie*.
- Keeping everything in memory
    - Disks have two significant advantages: they are durable, and they have lower cost per gigabyte than RAM.
    - Key-value stores, such as Memcached are intended for cache only, it's acceptable for data to be lost if the machine is restarted. Other in-memory databases aim for durability, with special hardware, writing a log of changes to disk, writing periodic snapshots to disk or by replicating in-memory sate to other machines.
    - Products such as VoltDB, MemSQL, and Oracle TimesTime are in-memory databases. Redis and Couchbase provide weak durability.
    - In-memory databases can be faster because they can avoid the overheads of encoding in-memory data structures in a form that can be written to disk.
    - Anti-cache

## Transaction processing or analytics?

<aside>
💡 A *transaction* is a group of reads and writes that form a logical unit, this pattern became known as ***online transaction processing* (OLTP)**. ***Data analytics*** has very different access patterns. A query would need to scan over a huge number of records, only **reading a few columns per record**, and **calculates aggregate statistics**. These queries are often written by business analysts, and fed into reports. This pattern became known for ***online analytics processing*(OLAP)**.

</aside>

|  | Transaction processing systems (OLTP) | Analytic systems (OLAP) |
| --- | --- | --- |
| Main read pattern
 | Small number of records per query, fetched by key
 | Aggregate over large number of records
 |
| Main write pattern
 | Random-access, low-latency writes from user input
 | Bulk import (ETL) or event stream
 |
| Primarily used by
 | End user/customer, via web application
 | Internal analyst, for decision support
 |
| What data represents
 | Latest state of data (current point in time)
 | History of events that happened over time
 |
| Dataset size | Gigabytes to terabytes | Terabytes to petabytes |

*Table 3-1. Comparing characteristics of transaction processing versus analytic systems*

*Table 3-1. Comparing characteristics of transaction processing versus analytic systems*

**Property**

Main read pattern
Main write pattern
Primarily used by
What data represents
Dataset size

**Transaction processing systems (OLTP)**

Small number of records per query, fetched by key
Random-access, low-latency writes from user input
End user/customer, via web application
Latest state of data (current point in time)
Gigabytes to terabytes

**Analytic systems (OLAP)**

Aggregate over large number of records
Bulk import (ETL) or event stream
Internal analyst, for decision support
History of events that happened over time
Terabytes to petabytes

- **Data warehousing**
    - A *data warehouse* is a separate database that analysts can query to their heart's content without affecting OLTP operations. It contains read-only copy of the dat in all various OLTP systems in the company. Data is extracted out of OLTP databases (through periodic data dump or a continuous stream of update), transformed into an analysis-friendly schema, cleaned up, and then loaded into the data warehouse (process *Extract-Transform-Load* or ETL).
    - A data warehouse is most commonly relational, but the internals of the systems can look quite different.
    - Amazon RedShift is hosted version of ParAccel. Apache Hive, Spark SQL, Cloudera Impala, Facebook Presto, Apache Tajo, and Apache Drill. Some of them are based on ideas from Google's Dremel.
    - Data warehouses are used in fairly formulaic style known as a *star schema*.

![截圖 2023-04-25 下午8.17.48.png](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/%25E6%2588%25AA%25E5%259C%2596_2023-04-25_%25E4%25B8%258B%25E5%258D%25888.17.48.png)

![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%202.png)

# Index

## Data Storage

For database data storage, there are usually two kinds of strategies, 

- tuple-oriented(page-oriented?)
    
    ![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%203.png)
    
- log-oriented
    
    ![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%204.png)
    

PostgreSQL uses a tuple-oriented approach with its heap-organized tables, while MySQL's InnoDB storage engine uses a clustered index to store data in a tuple-oriented manner. 

Log-structured storage systems like LSM trees are used in some NoSQL databases.

## Index  usage

For how MySQL uses index, please check the [resource](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848.md). 

And for Postgresql u can simply think all indexes were non-cluster index(secondary index), but instead of retrieving actual data from cluster index tree, PostgreSQL store data in a heap-organized table. 
Compared to the cluster index, it stores data without any order so that we can get actual data in a O(1) move.(without any order means data location can be fixed). And it’s faster in some cases cause we can avoid getting data from cluster index (b+ tree). 

But due to lack of locality, it is harder to get data when doing range queries.
Postgresql try to resolve latency that happened when using secondary index, cause most of bottleneck happened when using secondary index.   

### Stars and Snowflakes

![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%205.png)

- Many data warehouses are used in a fairly formulaic style, known as a star schema(aka. dimensional modeling)
    - fact table: fact_sales
        - recording events, e.g., page views / clicks
        - can be extremely large
        - columns: attributes / foreign key references to other dimension tables
    - dimension table: dim_product / dim_store / dim_date / dim_customer / dim_promotion
        - represent the who, what, where, when, how, and why of the event.
        - well-normalized?
- A variation of this template is known as the snowflake schema, where dimensions are
further broken down into sub-dimensions.
    
    ![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%206.png)
    

## Column-Oriented Storage

- It will become challenging when trillions of rows and petabytes of data in fact tables.
- under analytical contexts, we rarely need all columns-
    
    ![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%207.png)
    
- The idea of column-oriented storage:
    
    <aside>
    💡 Don’t store all the values from one row together, but store all the values from each column together instead.
    
    </aside>
    
- If each column is stored in a separate file, a query only needs to read and parse those columns
that are used in that query, which can save a lot of work.

![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%208.png)

### Column Compression

- Reduce the demands on disk: compressing data.
    - *bitmap encoding*
        - takes a column with n distinct values and turn it into n separate bitmaps.
        
        ![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%209.png)
        
    - very suited for queries in a data warehouse
        
        ```python
        WHERE product_sk IN (30, 68, 69)
        ```
        
        load the 3 bitmaps for product_sk = 30, product_sk 68, and product_sk = 69.
        
        Calculate the bitwise OR of the three bitmaps, which can be done very efficiently.
        
        ```bash
        WHERE product_sk = 31 AND store_sk = 3
        ```
        
        the columns contain the rows in the same order, so the *k*th bit in one column’s bitmap corresponds to the same row as the *k*th bit in another column’s bitmap.
        

### Memory bandwidth and vectorized processing

- bottlenecks may exist when
    - bandwidth for getting data from disk into memory.
    - bandwidth for data from *memory* into *CPU cache.*
        
        → single-instruction-multi-data (SIMD) instructions in modern CPUs.
        
- Vectorized processing
    - compressed column data that fits comfortably in the CPU L1 cache
    - Vectorized code makes efficient utilization of CPU cache. For example, consider a row of data with 10 columns and a query plan that needs to operate only on a single column. In a row-oriented query processing model, nine columns would occupy cache unnecessarily, limiting the number of values that can fit into cache. With column oriented processing, only the values from particular column of interest would be read into cache, allowing for many more values to be processed together and efficient usage of CPU-memory bandwidth.
        
        → helps with developing faster analytical query engines.
        

### Sort Order in Column-Storage

- Doesn’t necessarily matter but will help to use it as an indexing mechanism by choosing to impose an order.
    
    ![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%2010.png)
    
    - The administrator of the database can choose the columns by which the table should be sorted, using their knowledge of common queries. e.g., `date_key`
        
        → the query optimizer can scan only the rows from the last month, which will be much faster than scanning all rows.
        
    - A second column can determine the sort order of any rows that have the same value
    in the first column. e.g., `product_sk`
        
        → will help queries that need to group or filter sales by product within a certain date range.
        

### Writing to Column-Oriented Storage

- Column-oriented storage, compression, and sorting all help to make those read queries faster. However, they have the downside of making writes more difficult.
- A good Solution: LSM-trees.
    1. go to an in-memory store
    2. accumulate enough writes
    3. merged with the column files on disk and written to new files in bulk.
- Queries need to examine both the column data on disk and the recent writes in memory, and combine the two, but they are hidden from users.

### Aggregation: Data Cubes and Materialized Views

- Not every data warehouse is necessarily a column store: traditional row-oriented
databases and a few other architectures are also used. However, columnar storage can
be significantly faster for ad hoc analytical queries, so it is rapidly gaining popularity.
- it can be wasteful to involve an aggregate function, such as COUNT, SUM, AVG, MIN, or MAX in SQL every time → ***why not cache some of them?***
    - materialized view!

**Difference between views and material views**

| Views (virtual) | Material views |
| --- | --- |
| shortcut of queries | query results |
| stored in memory | write into disk |
| processes the queries when running | accessing the stored results |
| no need to refresh | need to refresh or rematerialized |
| OLAP | OLAP |

- A common special case of a materialized view is known as a *data cube* or *OLAP cube.*

![Untitled](Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848/Untitled%2011.png)

- may easily be more than 2 dimensions.
- pros: certain queries become very fast because they have effectively been precomputed.
- cons: doesn’t have the same flexibility as querying the raw data. e.g, proportions of sales.

## Summary

- Storage engines often falls into 2 categories
    
    
    | Transactional  (OLTP) | Analytics (OLAP) |
    | --- | --- |
    | User-facing → huge volume of user requests | Data warehouse |
    | small number of records in each query.  | demanding queries, millions of records are scanned in a short time |
    | storage engine use indexes to find the requested data | Disk bandwidth is often the bottleneck |
    | log-structured vs. update-in-place | Encode data very compactly to minimize the amount of data that need to read |

- when your queries require sequentially scanning across a large number of rows, indexes are much less relevant. Instead it becomes important to encode data very compactly, to minimize the amount of data that the query needs to read from disk. We discussed how column-oriented storage helps achieve this goal.