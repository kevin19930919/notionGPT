# Chapter 5. Replication

- **The difficulty** with replication lies in dealing with changes (changes) to replicated data. We'll discuss three popular change replication algorithms:
    - **Benefits** of replicating data:
        1. To bring data closer to users geographically (thus reducing latency).
        2. To ensure the system keeps functioning even if part of it fails (thus improving availability).
        3. To scale the number of machines that can handle read requests (thus increasing read throughput).
    1. single-leader
    2. multi-leader
    3. leaderless
- **Trade-offs to consider** when replicating, such as
    - synchronous replication or asynchronous replication
    - failed replicas handling
- Author murmuring…
    - outside of research, many developers still assume that a database has only one node. The shift towards distributed databases has happened relatively recently.
    - Discuss topics that often misunderstood, such as *eventual consistency, read-your-writes* and *monotonic read*.

## Leaders and Followers

- ***replica***: Each node that stores a copy of the database

> ***How to ensure that all data is present on all replicas?***
> 
> - leader-based replication
> - aka active/passive replication or master/slave replication

 Here's how it works:

![Screen Shot 2023-05-28 at 9.55.11 AM.png](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Screen_Shot_2023-05-28_at_9.55.11_AM.png)

1. Leader (master/primary)
    1. Requests must be sent to leader and leader will write to its local disk
2. Followers (read replicas/slaves/secondaries/hot-standby)
    1. Changes sent to followers after leader write → replication log or change stream
3. Clients read / write
    1. Read: query either the leader or any follower. 
    2. Write: **only the leader can accept write operations (from the client's perspective, the replicas are read-only).**

Usages: 

- **Relational databases**: PostgreSQL (starting from version 9.0), MySQL, Oracle Data Guard [2], and SQL Server's AlwaysOn Availability Groups
- **Non-relational databases**: MongoDB, RethinkDB, and Espresso
- **Distributed message brokers**: Kafka
- **High-availability queues**: RabbitMQ
- **Network file systems**: block replication devices like DRBD

### Synchronous Versus Asynchronous Replication

1. Synchronous: waits until respond success, ex: follower 1
2. Asynchronous: doesn’t wait, ex: follower 2

![Screen Shot 2023-05-30 at 10.19.31 PM.png](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Screen_Shot_2023-05-30_at_10.19.31_PM.png)

There are pros and cons between these two kind of steps:

1. Synchronous: higher latency, lack of part of availability, higher consistency
2. Asynchronous: lower latency, lack of consistency

Setups:

|  | pros | cons | Comments |
| --- | --- | --- | --- |
| Completely sync
(all nodes blocked) | - Guaranteed latest data 
- Available on the followers if lead failed | Could be blocked if 1 node doesn’t respond  | Impractical  |
| 1 follower set to sync | At least 2 replica of latest data |  | semi-synchronous |
| Completely async | Highly available on write  | Weak durability | Widely use on:
- Many followers
- geographically distributed |

### Setting Up New Followers

Why?

- increasing the number of replica
- replacing failed nodes

> How to ensure the new follower has an accurate copy?
*Do it from the DB side, not just copy the files from leader*
> 
1. Take a consistent snapshot without locking the entire DB
2. Copy the snapshot to the new node
3. Connect to the leader and **requests all the changes after the snapshot taken** (ex: PostgreSQL → log sequence number, MySQL → binlog coordinates)
4. After catching up, continue to process the data changes from leader 

### Handling node outage

> Achieving high availability with leader-based replication
***Reducing downtime as much as possible***
> 

- Follower failure → Catch-up recovery
    - Recover from data change log
    - request all the data changes during the disconnection
- (tricker) Leader failure → **Failover**
    - Promote one of the followers to be the new leader

Steps of failover automatically:

1. Determining that the leader has failed → timeout
2. Choosing the new leader 
    - election process, pre-selected node → the node with the most up-to-date data
3. Reconfiguring the system to use the new leader
    - Client send write requests to the new leader
    - Ensure the old leader becomes a follower if it came back

Things that can go wrong:

1. New leader might not have the most up-to-date data → async repilca 
2. Data conflict causing chain reactions of system goes wrong
3. Split brain: > 1 node believe that they are the leader
4. Hard to determine the right timeout time for leader not responding 

Some might prefer manually failover due to problems above. 

> **Replica consistency, durability, availability, latency**
→ Fundamental problems of distributed systems
> 

### **Implementation of Replication Logs**

How does leader-based replication work?  mainly 4 different methods.

1. **Statement-based replication**
    - statement: write requests to the leader
    - Leader sends statement log to the followers
    - Possible break down cause:
        1. nondeterministic function*, ex: Now(), RAND()*
        2. autoincrementing column*,* must be executed in the exact same order
        3. Statements with side effects. *e.g.,* triggers, stored procedures, user-defined functions (UDF)
2. **Write-ahead log (WAL) shipping** 
    - Sending logs to the followers:
        - log-structured storage engine: logs segments are compacted.
        - B-tree: write-ahead log → where modification is first  written to
    - Used in PostgreSQL, Oracle
    - Disadvantages:
        - highly coupled with DB engine & version
        - zero-downtime upgrade off table
3. **Logical (row-based) log replication**
    - logical-format: use different log formats for replication → allow the replication decouple from storage engine, ex: MySQL’s binlog
    - Logical format also used by external applications, because it’s easier to be parsed, ex: CDC
4. **Trigger-based replication**
    - replica not all data
    - Application code involved
    - big overhead (additional overhead to leader)
        
        Overhead explanation From ChatGPT :
        
        1. Increased Processing: Trigger-based replication relies on database triggers to capture changes made to a table and replicate them to other databases or systems. Whenever an operation (such as INSERT, UPDATE, or DELETE) occurs on the source table, the trigger fires, and its associated replication logic is executed. This additional processing introduces overhead compared to other replication methods that may operate at a lower level, such as log-based replication.
        2. Transactional Overhead: Triggers are executed within the context of a transaction. Each operation that triggers a replication event typically requires a transaction to ensure atomicity and consistency. This means that the replication system must manage transactional overhead, including transactional logging and synchronization, which can impact performance.
        3. Network Traffic: Trigger-based replication often involves transmitting the changes made to the source table over a network to the target systems. This introduces network traffic and can potentially impact the overall system performance, especially if the volume of changes is significant.
        4. Scalability Challenges: As the number of tables and triggers increase, the complexity of managing trigger-based replication also increases. Coordinating the firing of triggers, maintaining consistency, and managing dependencies can become challenging as the database grows, impacting the scalability of the replication solution.
        5. Maintenance and Troubleshooting: Triggers are additional database objects that require maintenance and monitoring. Debugging and troubleshooting trigger-related issues can be more complex compared to other replication methods, adding to the overhead of managing the replication system.

## **Problems with Replication Lag**

- Reasons for replication:
    - being able to node failures.
    - scalability (processing more requests)
    - latency (placing closer to users)
- An attractive option for mostly reads and small writes workloads → *read-scaling architecture*
    - Capacity for serving read-only requests simply by adding more followers.
    - only realistically works with asynchronous replication.
    - potential problems of an *asynchronous* follower → Replication lag
        - inconsistencies in the database.
        - followers fallen behind only a fraction of a second / seconds / minutes …
    

→ Three examples of problems that are likely to occur when there is replication lag and outline some approaches to solving them.

### 1. Reading Your Own writes.

the user views the data shortly after making a write, the new data may not yet have reached the replica. → misunderstood by the user.

![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled.png)

- We need *read-after-write consistency* (a.k.a. *read-your-writes consistency*): Users see any updates they submitted themselves, although it makes no promises about other users.
- Some possible techniques to implement read-after-write consistency:
    1. Read from leaders when something might have been modified. e.g., Users’ own profiles.
        1. Effective when something only editable by the owner of the profile.
    2. make all reads from the leader within one minute after the last update.
    3. Ensure that the replica serving any reads for that user reflects updates at least until the timestamp of client’s most recent write.
    4. Any request that needs to be served by the leader must be routed to the datacenter that contains the leader.
- A desktop web browser and a mobile app may got *cross-device read-after-write consistency* provided. (happens when a user enters some information on one device and then views it on another.) some additional issues:
    1. Approaches that require remembering the timestamp of the user’s last update become more difficult → metadata will need to be centralized.
    2. No guarantee of the same routed connections built for different devices across different datacenters.

### 2. Monotonic Reads

A user sees things moving backward in time.

happens when two same requests are routed to randomly-assigned servers.

![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%201.png)

- Monotonic reads is a guarantee that this kind of anomaly does not happen.
- Make sure users will not see time go backward - they will not read older data after having previously read newer data.

### 3. Consistent Prefix Reads

The third potential problems: ***violation of causality.***

![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%202.png)

- Preventing this kind of anomaly requires another type of guarantee: ***consistent prefix reads.***
    - ***consistent prefix reads:*** if a sequence of writes happens in a certain order, then anyone reading those writes will see them appear in the same order.
- This is a particular problem in partitioned (sharded) databases. If the database always applies writes in the same order, reads always see a consistent prefix, so this anomaly cannot happen. However, in many distributed databases, different partitions operate independently, so there is no global ordering of writes: when a user reads from the database, they may see some parts of the database in an older state and some in a newer state.
    - one solution: make sure that any writes that are causally related to each other are written to the same partition → somehow not efficient.

### Solutions for Replication Lag

- It’s worth thinking about how the application behaves if the replication lag increases to several minutes or even hours.
    - No problem. 大丈夫
    - bad for users. → provide a stronger guarantee, such as read-after-write/*consistent prefix reads*.
- It would be better if application developers didn’t have to worry about subtle replication
issues and could just trust their databases to “do the right thing.”
    
    → This is why ***transactions*** exist: they are a way for a database to provide stronger guarantees so that the application can be simpler.
    
- some solution discussed with the use of transaction in distributed databases.
    
    → Will be discussed in Chapter 7 and 9.
    

## Multi-Leader Replication

Leader-based replication has one major downside: there is noly **one** leader, and all writes must go through it. problems happen when one cannot connect to the leader for any reason.

A natural extension of the leader-based replication model: multi-leader configuration (a.k.a. master–master or active/active replication).

### Use Cases for Multi-Leader Replication

Some situations make this configuration be reasonable:

**Multi-datacenter operation**

configure a leader in each datacenter.

![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%203.png)

- Performance
    - A single-leader configuration can add significant latency to writes.
    - In a multi-leader configuration, every write can be processed in the local datacenter and is replicated asynchronously to the other datacenters.
- Tolerance of datacenter outages
    - In a single-leader configuration, if the datacenter with the leader fails, failover can promote a follower in another datacenter to be leader.
    - In a multi-leader configuration, each datacenter can continue operating independently of the others, and replication catches up when the failed datacenter comes back online.
- Tolerance of network problems
    - A single-leader configuration is very sensitive to problems in this inter-datacenter link, because writes are made synchronously over this link.
    - A multi-leader configuration with asynchronous replication can usually tolerate network problems better: a temporary network interruption does not prevent writes being processed.

Some databases support multi-leader configuration by default. It is also often implemented with external tools, such as Tungsten Replicator for **MySQL**, BDR for **PostgreSQL**, and GoldenGate for **Oracle**.

A Potential downside: data may be concurrently modified in two different datacenters → conflict!!

Hence, it’s often been considered dangerous and should be avoided if possible.

**Clients with offline operation**

- Another situation in which multi-leader replication is appropriate is if app needs to continue to work while disconnected. e.g., calendar app
    - every device has a local database that acts as a leader (accept write requests.)
    - sync when reconnect to the internet.

**Collaborative editing**

- Real-time collaborative editing applications allow several people to edit a document simultaneously.
    - Well-known example: Google Docs.
    - Allow people concurrently edit a text document or spreadsheet
- When one user edits a document, the changes are instantly applied to their local replica (the
state of the document in their web browser or client application) and asynchronously
replicated to the server and any other users who are editing the same document.
- Avoid editing conflict → lock when one is editing until committed changes.
- However, for faster collaboration, you may want to make the unit of change very
small (e.g., a single keystroke) and avoid locking. This approach allows multiple users
to edit simultaneously, but it also brings all the challenges of multi-leader replication,
including requiring conflict resolution

### **Handling Write Conflicts**

- The biggest problem with multi-leader replication is that write conflicts

![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%204.png)

**Synchronous versus asynchronous conflict detection**

- single leader: the second writer will either block and wait for the first
write to complete, or abort the second write transaction, forcing the user to retry the
write.
- multi-leader: both writes are successful, and the
conflict is only detected asynchronously at some later point in time. At that time, it
may be too late to ask the user to resolve the conflict
- if making the conflict detection synchronous—i.e., wait for the
write to be replicated to all replicas before telling the user that the write was successful. which can solve issue but losing the advantage of multi-leader —> allowing each replica to accept writes independently

**Conflict avoidance**

- simplest strategy: if the application can
ensure that all writes for a particular record go through the same leader, then conflicts
cannot occur.
    - For example, in an application where a user can edit their own data, you can ensure
    that requests from a particular user are always routed to the same datacenter and use
    the leader in that datacenter for reading and writing. Different users may have different
    “home” datacenters (perhaps picked based on geographic proximity to the user),
    but from any one user’s point of view the configuration is essentially single-leader.
    - However, sometimes you might want to change the designated leader for a record—
    perhaps because one datacenter has failed and you need to reroute traffic to another
    datacenter, or perhaps because a user has moved to a different location and is now
    closer to a different datacenter. In this situation, conflict avoidance breaks down, and
    you have to deal with the possibility of concurrent writes on different leaders.
    
    **Converging toward a consistent state**
    
    A **single-leader database** applies writes in a sequential order: if there are several
    updates to the same field, the last write determines the final value of the field.
    In a **multi-leader configuration**, there is no defined ordering of writes, so it’s not clear
    what the final value should be.
    
    every replication scheme must ensure that the data is eventually the same in all replicas. Thus, the database must resolve the conflict in a convergent way, which means that **all replicas must arrive at the same final value when all changes have been replicated.**
    There are various ways of achieving convergent conflict resolution:
    • Give each write a unique ID (e.g., a timestamp, a long random number, a UUID,
    or a hash of the key and value), pick the write with the highest ID as the winner,
    and throw away the other writes. If a timestamp is used, this technique is known
    as last write wins (LWW). Although this approach is popular, it is dangerously
    prone to data loss 
    • Give each replica a unique ID, and let writes that originated at a higher numbered
    replica always take precedence over writes that originated at a lower numbered
    replica. This approach also implies data loss.
    • Somehow merge the values together—e.g., order them alphabetically and then
    concatenate them (in Figure 5-7, the merged title might be something like
    “B/C”).
    • Record the conflict in an explicit data structure that preserves all information,
    and write application code that resolves the conflict at some later time (perhaps
    by prompting the user).
    
    **Custom conflict resolution logic**
    
    multi-leader replication tools let you write conflict resolution logic using application
    code.
    
    - On write
    As soon as the database system detects a conflict in the log of replicated changes,
    it calls the conflict handler. For example, Bucardo allows you to write a snippet of
    Perl for this purpose. This handler typically cannot prompt a user—it runs in a
    background process and it must execute quickly.
    - On read
    When a conflict is detected, all the conflicting writes are stored. The next time
    the data is read, these multiple versions of the data are returned to the application.
    The application may prompt the user or automatically resolve the conflict,
    and write the result back to the database. CouchDB works this way, for example.
    
    Note that conflict resolution usually applies **at the level of an individual row or document,** not for an entire transaction. Thus, if you have a transaction that atomically makes several different writes (see Chapter 7), each write is still considered
    separately for the purposes of conflict resolution.
    
    **Automatic Conflict Resolution**
    Conflict resolution rules can quickly become complicated, and custom code can be
    error-prone. Amazon is a frequently cited example of surprising effects due to a conflict
    resolution handler: for some time, the conflict resolution logic on the shopping
    cart would preserve items added to the cart, but not items removed from the cart.
    Thus, customers would sometimes see items reappearing in their carts even though
    they had previously been removed [37].
    There has been some interesting research into automatically resolving conflicts
    caused by concurrent data modifications. A few lines of research are worth mentioning:
    • **Conflict-free replicated datatypes (CRDTs)**: are a family of data structures
    for sets, maps, ordered lists, counters, etc. that can be concurrently edited by
    multiple users, and which automatically resolve conflicts in sensible ways. Some
    CRDTs have been implemented in Riak 2.0 [39, 40].
    • **Mergeable persistent data structures** track history explicitly, similarly to the
    Git version control system, and use a three-way merge function (whereas CRDTs
    use two-way merges).
    • **Operational transformation** is the conflict resolution algorithm behind collaborative
    editing applications such as Etherpad [30] and Google Docs [31]. It
    was designed particularly for concurrent editing of an ordered list of items, such
    as the list of characters that constitute a text document.
    
    **What is a conflict?**
    
    Some kinds of conflict are obvious. In the example in Figure 5-7, two writes concurrently
    modified the same field in the same record, setting it to two different values.
    There is little doubt that this is a conflict.
    Other kinds of conflict can be more subtle to detect. For example, consider a meeting
    room booking system: it tracks which room is booked by which group of people at
    which time. This application needs to ensure that each room is only booked by one
    group of people at any one time (i.e., there must not be any overlapping bookings for
    the same room). In this case, a conflict may arise if two different bookings are created
    for the same room at the same time. Even if the application checks availability before allowing a user to make a booking, there can be a conflict if the two bookings are made on two different leaders.
    There isn’t a quick ready-made answer, but in the following chapters we will trace a
    path toward a good understanding of this problem. We will see some more examples
    of conflicts in Chapter 7, and in Chapter 12 we will discuss scalable approaches for
    detecting and resolving conflicts in a replicated system.
    
    ### **Multi-Leader Replication Topologies**
    
    A replication topology describes the communication paths along which writes are
    propagated from one node to another. With more than two leaders, various different topologies are possible.
    Some examples are illustrated in Figure 5-8.
    
    Figure 5-8. Three example topologies in which multi-leader replication can be set up.
    
    ![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%205.png)
    
    **The most general topology is all-to-all** (Figure 5-8 [c]), in which every leader sends its
    writes to every other leader. However, more restricted topologies are also used: for
    example, **MySQL by default supports only a circular topology** [34], in which each
    node receives writes from one node and forwards those writes (plus any writes of its
    own) to one other node. Another popular topology has the shape of a star:v one designated
    root node forwards writes to all of the other nodes. The star topology can be
    generalized to a tree.
    
    In circular and star topologies, a write may need to pass through several nodes before
    it reaches all replicas. Therefore, nodes need to forward data changes they receive
    from other nodes. **To prevent infinite replication loops, each node is given a unique
    identifier**, and in the replication log, each write is tagged with the identifiers of all the
    nodes it has passed through [43]. When a node receives a data change that is tagged
    
    with its own identifier, that data change is ignored, because the node knows that it
    has already been processed.
    
    A problem with circular and star topologies is that if just one node fails, it can interrupt
    the flow of replication messages between other nodes, causing them to be unable
    to communicate until the node is fixed. The topology could be reconfigured to work
    around the failed node, but in most deployments such reconfiguration would have to
    be done manually. The fault tolerance of a more densely connected topology (such as
    all-to-all) is better because
    
    On the other hand, all-to-all topologies can have issues too. In particular, some network
    links may be faster than others (e.g., due to network congestion), with the result
    that some replication messages may “overtake” others, as illustrated in Figure 5-9.
    
    ![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%206.png)
    
    Figure 5-9. With multi-leader replication, writes may arrive in the wrong order at some
    replicas.
    
    In Figure 5-9, client A inserts a row into a table on leader 1, and client B updates that
    row on leader 3. However, leader 2 may receive the writes in a different order: it may
    first receive the update (which, from its point of view, is an update to a row that does
    not exist in the database) and only later receive the corresponding insert (which
    should have preceded the update).
    
    This is a problem of causality, similar to the one we saw in “Consistent Prefix Reads”
    on page 165: the update depends on the prior insert, so we need to make sure that all
    nodes process the insert first, and then the update**. Simply attaching a timestamp to every write is not sufficient, because clocks cannot be trusted to be sufficiently in sync**
    to correctly order these events at leader 2 (see Chapter 8).
    To order these events correctly, a technique called **version vectors** can be used, which
    we will discuss later in this chapter (see “Detecting Concurrent Writes” on page 184).
    However, conflict detection techniques are poorly implemented in many multi-leader
    replication systems. For example, at the time of writing, PostgreSQL BDR does not
    provide causal ordering of writes [27], and Tungsten Replicator for MySQL doesn’t
    even try to detect conflicts [34].
    If you are using a system with multi-leader replication, it is worth being aware of
    these issues, carefully reading the documentation, and thoroughly testing your database
    to ensure that it really does provide the guarantees you believe it to have.
    
    **Leaderless Replication**
    The replication approaches we have discussed so far in this chapter—single-leader
    and multi-leader replication—are based on the idea that a client sends a write request
    to one node (the leader), and the database system takes care of copying that write to
    the other replicas. A leader determines the order in which writes should be processed,
    and followers apply the leader’s writes in the same order.
    Some data storage systems take a different approach, abandoning the concept of a
    leader and allowing any replica to directly accept writes from clients. this kind of database is also known as Dynamo-style.
    **In some leaderless implementations, the client directly sends its writes to several replicas,
    while in others, a coordinator node does this on behalf of the client. However,
    unlike a leader database, that coordinator does not enforce a particular ordering of
    writes.** As we shall see, this difference in design has profound consequences for the
    way the database is used.
    
    **Writing to the Database When a Node Is Down**
    
    Imagine you have a database with three replicas, and one of the replicas is currently
    unavailable—perhaps it is being rebooted to install a system update. In a leader-based 
    
    configuration, if you want to continue processing writes, you may need to perform a
    failover (see “Handling Node Outages” on page 156).
    
    On the other hand, **in a leaderless configuration, failover does not exist.** Figure 5-10
    shows what happens: the client (user 1234) sends the write to all three replicas in parallel,
    and the two available replicas accept the write but the unavailable replica misses
    it. Let’s say that it’s sufficient for two out of three replicas to acknowledge the write:
    after user 1234 has received two ok responses, we consider the write to be successful.
    The client simply ignores the fact that one of the replicas missed the write.
    
    ![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%207.png)
    
    Figure 5-10. A quorum write, quorum read, and read repair after a node outage.
    
    Now imagine that the unavailable node comes back online, and clients start reading
    from it. Any writes that happened while the node was down are missing from that
    node. Thus, if you read from that node, you may get stale (outdated) values as
    responses.
    To solve that problem, when a client reads from the database, it doesn’t just send its
    request to one replica: read requests are also sent to several nodes in parallel. The client
    may get different responses from different nodes; i.e., the up-to-date value from
    one node and a stale value from another. Version numbers are used to determine
    which value is newer (see “Detecting Concurrent Writes” on page 184).
    
    **Read repair and anti-entropy**
    The replication scheme should ensure that eventually all the data is copied to every
    replica. After an unavailable node comes back online, how does it catch up on the
    writes that it missed?
    
    Two mechanisms are often used in Dynamo-style datastores:
    ***Read repair***
    When a client makes a read from several nodes in parallel, it can detect any stale
    responses. For example, in Figure 5-10, user 2345 gets a version 6 value from replica
    3 and a version 7 value from replicas 1 and 2. The client sees that replica 3
    has a stale value and writes the newer value back to that replica. This approach
    works well for values that are frequently read.
    ***Anti-entropy process***
    In addition, some datastores have a background process that constantly looks for
    differences in the data between replicas and copies any missing data from one
    replica to another. **Unlike the replication log in leader-based replication, this
    anti-entropy process does not copy writes in any particular order, and there may
    be a significant delay before data is copied.**
    Not all systems implement both of these; for example, Voldemort currently does not
    have an anti-entropy process. **Note that without an anti-entropy process, values that
    are rarely read may be missing from some replicas and thus have reduced durability**,
    because read repair is only performed when a value is read by the application.
    
    ## Quorums for reading and writing
    
    In the example of Figure 5-10, we considered the write to be successful even though it
    was only processed on two out of three replicas. What if only one out of three replicas
    accepted the write? ****How far can we push this?
    
    More generally, if there are n replicas, every write must be confirmed by w nodes to
    be considered successful, and we must query at least r nodes for each read. (In our
    example, n = 3, w = 2, r = 2.) As long as w + r > n, we expect to get an up-to-date
    value when reading, because at least one of the r nodes we’re reading from must be
    up to date. Reads and writes that obey these r and w values are called quorum reads
    and writes [44]. You can think of r and w as the minimum number of votes required
    for the read or write to be valid.
    
    In Dynamo-style databases, the parameters n, w, and r are typically configurable. A
    common choice is to make n an odd number (typically 3 or 5) and to set w = r =
    (n + 1) / 2 (rounded up). However, you can vary the numbers as you see fit. For
    example, a workload with few writes and many reads may benefit from setting w = n
    and r = 1. This makes reads faster, but has the disadvantage that just one failed node
    causes all database writes to fail.
    
    The quorum condition, **w + r > n,** allows the system to tolerate unavailable nodes as
    follows:
    
    - If w < n, we can still process writes if a node is unavailable.
    - If r < n, we can still process reads if a node is unavailable.
    - With n = 3, w = 2, r = 2 we can tolerate one unavailable node.
    - With n = 5, w = 3, r = 3 we can tolerate two unavailable nodes. This case is illus‐
    trated in Figure 5-11.
    - Normally, reads and writes are always sent to all n replicas in parallel. The
    parameters w and r determine how many nodes we wait for—i.e., how many of
    the n nodes need to report success before we consider the read or write to be suc‐
    cessful.
    
    ![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%208.png)
    
    If fewer than the required w or r nodes are available, writes or reads return an error.
    A node could be unavailable for many reasons:
    
    - the node is down (crashed, powered down)
    - due to an error executing the operation (can’t write because the disk is full)
    - due to a network interruption between the client and the node
    - or for any number of other reasons.
    
    ## **Limitations of Quorum Consistency**
    
    <aside>
    💡 Quorum condition might not be as powerful as it looks.
    
    </aside>
    
    Often, r and w are chosen to be a majority (more than n/2) of nodes, because that
    ensures w + r > n while still tolerating up to n/2 node failures. But quorums are not
    necessarily majorities—it only matters that the sets of nodes used by the read and
    write operations overlap in at least one node. Other quorum assignments are possi‐
    ble, which allows some flexibility in the design of distributed algorithms [45].
    
    You may also set w and r to smaller numbers, so that w + r ≤ n (i.e., the quorum con‐
    dition is not satisfied). In this case, reads and writes will still be sent to n nodes, but a
    smaller number of successful responses is required for the operation to succeed.
    With a smaller w and r you are more likely to read stale values, because it’s more
    likely that your read didn’t include the node with the latest value. On the upside, this
    configuration allows lower latency and higher availability: if there is a network inter‐
    ruption and many replicas become unreachable, there’s a higher chance that you can
    continue processing reads and writes. Only after the number of reachable replicas
    falls below w or r does the database become unavailable for writing or reading,
    respectively.
    
    However, even with w + r > n, there are likely to be edge cases where stale values are
    returned. These depend on the implementation, but possible scenarios include:
    
    - If a sloppy quorum is used (see “Sloppy Quorums and Hinted Handoff” on page
    183), the w writes may end up on different nodes than the r reads, so there is no
    longer a guaranteed overlap between the r nodes and the w nodes
    - If two writes occur concurrently, it is not clear which one happened first. In this
    case, the only safe solution is to merge the concurrent writes (see “Handling
    Write Conflicts” on page 171). If a winner is picked based on a timestamp (last
    write wins), writes can be lost due to clock skew [35]. We will return to this topic
    in “Detecting Concurrent Writes” on page 184.
    - If a write happens concurrently with a read, the write may be reflected on only
    some of the replicas. In this case, it’s undetermined whether the read returns the
    old or the new value.
    - If a write succeeded on some replicas but failed on others (for example because
    the disks on some nodes are full), and overall succeeded on fewer than w replicas,
    it is not rolled back on the replicas where it succeeded. This means that if a write
    was reported as failed, subsequent reads may or may not return the value from
    that write [47].
    - If a node carrying a new value fails, and its data is restored from a replica carry‐
    ing an old value, the number of replicas storing the new value may fall below w,
    breaking the quorum condition.
    - Even if everything is working correctly, there are edge cases in which you can get
    unlucky with the timing, as we shall see in “Linearizability and quorums” on
    page 334.
    
    Thus, although quorums appear to guarantee that a read returns the latest written
    value, in practice it is not so simple. Dynamo-style databases are generally optimized
    for use cases that can tolerate eventual consistency.
    
    In particular, you usually do not get the guarantees discussed in “Problems with Rep‐
    lication Lag” on page 161 (reading your writes, monotonic reads, or consistent prefix
    reads), so the previously mentioned anomalies can occur in applications. Stronger
    guarantees generally require transactions or consensus. We will return to these topics
    in Chapter 7 and Chapter 9.
    
    ## Monitoring staleness
    
    <aside>
    💡 it’s important to monitor whether your databases are returning up-to-date results.
    
    </aside>
    
    For leader-based replication, the database typically exposes metrics for the replication
    lag, which you can feed into a monitoring system. This is possible because writes are
    applied to the leader and to followers in the same order, and each node has a position
    in the replication log (the number of writes it has applied locally). By subtracting a
    follower’s current position from the leader’s current position, you can measure the
    amount of replication lag.
    
    However, in systems with leaderless replication, there is no fixed order in which
    writes are applied, which makes monitoring more difficult. Moreover, if the database only uses read repair (no anti-entropy), there is no limit to how old a value might be
    —if a value is only infrequently read, the value returned by a stale replica may be
    ancient.
    
    There has been some research on measuring replica staleness in databases with lead‐
    erless replication and predicting the expected percentage of stale reads depending on
    the parameters n, w, and r [48]. This is unfortunately not yet common practice, but it
    would be good to include staleness measurements in the standard set of metrics for
    databases. Eventual consistency is a deliberately vague guarantee, but for operability
    it’s important to be able to quantify “eventual.”
    
    ## Sloppy Quorums and Hinted Handoff
    
    <aside>
    💡 An extended quorum condition that increases the write availability.
    
    </aside>
    
    Databases with appropriately configured quorums can tolerate the failure of individ‐
    ual nodes without the need for failover. They can also tolerate individual nodes going
    slow, because requests don’t have to wait for all n nodes to respond—they can return
    when w or r nodes have responded. These characteristics make databases with leader‐
    less replication appealing for use cases 
    
    - require high availability and low latency
    - can tolerate occasional stale reads
    
    However, quorums (as described so far) are not as fault-tolerant as they could be. A
    network interruption can easily cut off a client from a large number of database
    nodes. Although those nodes are alive, and other clients may be able to connect to
    them, to a client that is cut off from the database nodes, they might as well be dead. In
    this situation, it’s likely that fewer than w or r reachable nodes remain, so the client
    can no longer reach a quorum.
    
    In a large cluster (with significantly more than n nodes) it’s likely that the client can
    connect to some database nodes during the network interruption, just not to the
    nodes that it needs to assemble a quorum for a particular value. In that case, database
    designers face a trade-off:
    
    - Is it better to return errors to all requests for which we cannot reach a quorum of
    w or r nodes?
    - Or should we accept writes anyway, and write them to some nodes that are
    reachable but aren’t among the n nodes on which the value usually lives?
    
    The latter is known as a sloppy quorum [37]: writes and reads still require w and r
    successful responses, but those may include nodes that are not among the designated
    n “home” nodes for a value. By analogy, if you lock yourself out of your house, you
    may knock on the neighbor’s door and ask whether you may stay on their couch tem‐
    porarily.
    
    Once the network interruption is fixed, any writes that one node temporarily
    accepted on behalf of another node are sent to the appropriate “home” nodes. This is called hinted handoff. (Once you find the keys to your house again, your neighbor
    politely asks you to get off their couch and go home.)
    
    - a sloppy quorum actually isn’t a quorum at all in the traditional sense. It’s only
    an assurance of durability(eventual consistency?)
    - There is no guarantee that a read of r nodes will see it until the hinted handoff has
    completed.
    
    Benefits
    
    - Increase write availability
    
    Sloppy quorums are optional in all common Dynamo implementations. In Riak they
    are enabled by default, and in Cassandra and Voldemort they are disabled by default
    
    ### Multi-datacenter operation
    
    We previously discussed cross-datacenter replication as a use case for multi-leader
    replication (see “Multi-Leader Replication” on page 168). Leaderless replication is
    also suitable for multi-datacenter operation, since it is designed to tolerate 
    
    - conflicting concurrent writes
    - network interruptions
    - and latency spikes.
    
    Cassandra and Voldemort implement their multi-datacenter support within the normal leaderless model: 
    
    - n nodes in all datacenters
    - in the configuration, you can specify how many of the n replicas you want to have in each datacenter.
    - Each write from a client is sent to all replicas, regardless of datacenter, but the client usually only waits for acknowledgment from a quorum of nodes within its local datacenter so that it is unaffected by delays and interruptions on the cross-datacenter link.
    - The higher-latency writes to other datacenters are often configured to happen asynchronously, although there is some flexibility in the configuration [50, 51].
    
    Riak keeps all communication between clients and database nodes local to one data‐
    center
    
    - so n nodes within one datacenter.
    - Cross-datacenter replication between database clusters happens asynchronously in the background, in a style that is similar to multi-leader replication [52].
    
    ## Detecting Concurrent Writes
    
    Dynamo-style databases allow several clients to concurrently write to the same key,
    which means that conflicts will occur even if strict quorums are used.
    
    The problem is that events may arrive in a different order at different nodes, due to
    variable network delays and partial failures.
    
    For example, Figure 5-12 shows two clients, A and B, simultaneously writing to a key X in a three-node datastore:
    
    - Node 1 receives the write from A, but never receives the write from B due to a transient outage.
    - Node 2 first receives the write from A, then the write from B.
    - Node 3 first receives the write from B, then the write from A.
    
    ![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%209.png)
    
    Figure 5-12. Concurrent writes in a Dynamo-style datastore: there is no well-defined
    ordering.
    
    If each node simply overwrote the value for a key whenever it received a write request
    from a client, the nodes would become permanently inconsistent.
    
    How do replicas converge to the same value?
    
    - One might hope that replicated databases would handle this automatically, but unfortunately most implementations are quite poor
    - if you want to avoid losing data, you—the application developer—need to know a lot
    about the internals of your database’s conflict handling
    
    <aside>
    💡 Next, explore the issues in a bit more detail
    
    </aside>
    
    ### Last write wins (discarding concurrent writes)
    
    One approach for achieving eventual convergence is to declare that each replica need
    only store the most “recent” value and allow “older” values to be overwritten and dis‐
    carded. Then, as long as we have some way of unambiguously determining which
    write is more “recent,” and every write is eventually copied to every replica, the repli‐
    cas will eventually converge to the same value. But,
    
    - This idea “recent” is actually quite misleading
    - it doesn’t really make sense to say that either happened “first”: we say the writes
    are concurrent, so their order is undefined.
    
    Even though the writes don’t have a natural ordering, we can force an arbitrary order
    on them. For example, 
    
    - we can attach a timestamp to each write, pick the biggest timestamp as the most “recent,” and discard any writes with an earlier timestamp.
    - This conflict resolution algorithm, called last write wins (LWW), is the only supported conflict resolution method in Cassandra [53], and an optional feature in Riak
    
    ### The “happens-before” relationship and concurrency
    
    <aside>
    💡 How do we decide whether two operations are concurrent or not?
    
    → Two operations are concurrent if neither happens before the other(neither knows about the other)
    
    </aside>
    
    Let’s compare figure 5-9 and 5-12
    
    - In Figure 5-9, the two writes are not concurrent: A’s insert happens before B’s
    increment, because the value incremented by B is the value inserted by A. In
    other words, B’s operation builds upon A’s operation, so B’s operation must have
    happened later. We also say that B is causally dependent on A.
        - 
            
            ![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%2010.png)
            
    
    - the two writes in Figure 5-12 are concurrent: when each client starts the operation, it does not know that another client is also performing an operation on the same key. Thus, there is no causal dependency between the operations.
        - 
            
            ![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%2011.png)
            
    
    Thus, whenever you have two operations A and B, there are three possibilities:
    
    - A happened before B (B must know A)
    - B happened before A (A must know B)
    - A and B are concurrent
    
    ### Capturing the happens-before relationship
    
    1. Client 1 adds “milk” to the cart
    Client 1 sends [milk]
    with no version number
    receives version number 1
    2. Client 2 adds “eggs” to the cart
    Client 2 sends [eggs]
    with no version number
    receives version number 2
    3. Client 1 wants to add “flour” to the cart
    Client 1 sends [milk, flour]
    with version number 1
    receives version number 3
    4. client 2 wants to add “ham” to the cart
    Client 2 sends [eggs, milk, ham]
    with version number 2
    receives version number 4
    5. client 1 wants to add “bacon” 
    client 1 sends [milk, flour, eggs, bacon]
    with the version number 3
    receives version numbers 5
    
    ![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%2012.png)
    
    Figure 5-13. Capturing causal dependencies between two clients concurrently editing a
    shopping cart.
    
    The dataflow between the operations in Figure 5-13 is illustrated graphically in
    Figure 5-14. The arrows indicate which operation happened before which other operation, in the sense that the later operation knew about or depended on the earlier one.
    
    - old versions of the value do get overwritten eventually
    - no writes are lost.
    
    ![Untitled](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Untitled%2013.png)
    
    Figure 5-14. Graph of causal dependencies in Figure 5-13
    
    Note that the server can determine whether two operations are concurrent by looking at the version numbers—it does not need to interpret the value itself (so the value
    could be any data structure). The algorithm works as follows:
    
    The server maintains a version number for every key, increments the version
    number every time that key is written, and stores the new version number along
    with the value written.
     
    
    - When a client reads a key, the server returns all values that have not been over‐
    written, as well as the latest version number. A client must read a key before
    writing.
    - When a client writes a key, it must include the version number from the prior
    read, and it must merge together all values that it received in the prior read. (The
    response from a write request can be like a read, returning all current values,
    which allows us to chain several writes like in the shopping cart example.)
    - When the server receives a write with a particular version number, it can over‐
    write all values with that version number or below (since it knows that they have
    been merged into the new value), but it must keep all values with a higher ver‐
    sion number (because those values are concurrent with the incoming write).
    
    ### Merging concurrently written values
    
    <aside>
    💡 Extra work for clients when this solution is applied
    
    </aside>
    
    This algorithm ensures that no data is silently dropped, but it unfortunately requires
    that the clients do some extra work: if several operations happen concurrently, clients
    have to clean up afterward by merging the concurrently written values. Riak calls
    these concurrent values siblings.
    
    With the example of a shopping cart, a reasonable approach to merging siblings is to
    just take the union. In Figure 5-14, the two final siblings are [milk, flour, eggs,
    bacon] and [eggs, milk, ham]; note that milk and eggs appear in both, even
    though they were each only written once. The merged value might be something like
    [milk, flour, eggs, bacon, ham], without duplicates.
    
    <aside>
    💡 union is simple, how about remove?
    
    </aside>
    
    However, if you want to allow people to also remove things from their carts, and not
    just add things, then taking the union of siblings may not yield the right result: if you
    merge two sibling carts and an item has been removed in only one of them, then the
    removed item will reappear in the union of the siblings [37]. To prevent this problem,
    an item cannot simply be deleted from the database when it is removed; instead,
    the system must leave a marker with an appropriate version number to indicate that
    the item has been removed when merging siblings. Such a deletion marker is known
    as a tombstone. (We previously saw tombstones in the context of log compaction in
    “Hash Indexes” on page 72.)
    
    As merging siblings in application code is complex and error-prone, there are some
    efforts to design data structures that can perform this merging automatically, as dis‐
    cussed in “Automatic Conflict Resolution” on page 174. For example, Riak’s datatype
    support uses a family of data structures called CRDTs [38, 39, 55] that can automati‐
    cally merge siblings in sensible ways, including preserving deletions.
    
    ### Version vectors
    
    ![Screen Shot 2023-06-27 at 10.00.20 PM.png](Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60/Screen_Shot_2023-06-27_at_10.00.20_PM.png)
    
    Figure 5-13 uses a single version number to capture dependencies between opera‐
    tions, but that is not sufficient when there are multiple replicas accepting writes con‐
    currently. Instead, we need to use a version number per replica as well as per key.
    Each replica increments its own version number when processing a write, and also
    keeps track of the version numbers it has seen from each of the other replicas. This
    information indicates which values to overwrite and which values to keep as siblings.
    
    Like the version numbers in Figure 5-13, version vectors are sent from the database
    replicas to clients when values are read, and need to be sent back to the database
    when a value is subsequently written. (Riak encodes the version vector as a string that
    it calls causal context.) The version vector allows the database to distinguish between
    overwrites and concurrent writes.