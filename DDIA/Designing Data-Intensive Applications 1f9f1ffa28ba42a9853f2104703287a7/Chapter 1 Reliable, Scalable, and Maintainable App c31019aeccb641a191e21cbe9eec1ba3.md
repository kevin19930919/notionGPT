# Chapter 1. Reliable, Scalable, and Maintainable Applications

# Overview

The chapter emphasizes the need for applications to be:

1. **Reliability**: The system should continue to work correctly, even in the face of hardware or software failures, as well as human errors.
2. **Scalability**: As the system grows, it should be able to accommodate increased load without significantly impacting performance.
3. **Maintainability**: The system should be easy to evolve, debug, and manage over time, enabling a team to work effectively on it.

And introduces the idea of data systems, which are composed of databases, caches, search indexes, stream or batch processing, and other components that store and process data. The chapter briefly covers the various types of data systems and their respective roles.

![Screen Shot 2023-04-01 at 1.03.17 PM.png](Chapter%201%20Reliable,%20Scalable,%20and%20Maintainable%20App%20c31019aeccb641a191e21cbe9eec1ba3/Screen_Shot_2023-04-01_at_1.03.17_PM.png)

- Database - Store data for later use
- Cache - Remember the results of some very "heavy" operations to speed up read access later
- Message Queue - Deliver and distribute messages
- Search Engine - Allows users to search with various keywords and filter data with different conditions, ex: 歷史訊息搜索, logging
- Stream Processing - Continuously generate data and send it to other processes for processing
- Batch Processing - Periodically process accumulated large amounts of data

When designing a data system, there are many technical trade-offs, and various options for different components. What criteria should be used to evaluate the quality of a system? Here are three important indicators:

1. Reliability
2. Scalability
3. Maintainability

## Reliability

How to measure reliability?

- Functionality:
    
    Under normal circumstances, the application behavior meets the behavior given by the API.
    Proper handling of user input errors or incorrect operations.
    
- Performance:
    
    Able to meet promised performance indicators under given hardware and data volume.
    
- Security:
    
    Able to prevent unauthorized and malicious damage.
    

Two  concepts: 

1. Fault: Part of a system's state deviating from its standard
2. Failure: When the system as a whole stops providing services to users.

Systems without fault tolerance can easily fail when faults accumulate.

### Hardware failures

- Hard drive aging and bad sectors
- Memory failure
- Machine overheating causing CPU problems
- Power outage in the data center

### Software errors

- Unable to handle specific inputs, causing system crash.
- Out-of-control processes  consuming CPU, memory, and network resources.
- System-dependent components slowing down or becoming unresponsive.
- Cascading failures.

Although there is no quick fix for systemic failures in software, there are still many small measures we can take, such as:

1. Carefully considering assumptions and interactions within the system.
2. Thorough testing.
3. Process isolation.
4. Allowing processes to crash and restart.
5. Measuring, monitoring, and analyzing system behavior in production environments.

If the system can provide some guarantees (e.g., in a message queue, the number of incoming and outgoing messages is equal), then it can continuously self-check during operation and raise an alarm when discrepancies occur.

### Human factors

The most unstable part of the system is people, so it is important to minimize human impact on the system at the design level. Based on the software lifecycle, consider several stages:

- Design and coding
    - Eliminate all unnecessary assumptions, provide reasonable abstractions, and carefully design APIs.
    - Isolate processes and use sandbox mechanisms for particularly error-prone modules.
    - Implement circuit breaker design for service dependencies.
- Testing phase
    - Introduce third-party testers as much as possible and try to automate the testing platform.
    - Unit testing, integration testing, e2e testing, and chaos testing.
- Operation phase
    - Detailed dashboard.
    - Continuous self-inspection.
    - Alarm mechanism.
    - Contingency plans.
    - Scientific training and management for the organization.

## Scalability

Scalability refers to a system's ability to cope with increased load. It is important but challenging to achieve in practice due to a fundamental contradiction: **only products that survive have the opportunity to discuss scalability, while those designed too early for scalability often don't survive.**

However, understanding some basic concepts can help prepare for potential surges in load.

### Measuring Load

Before addressing load, it is essential to find appropriate ways to measure it, such as load parameters:

1. Daily and monthly active users for the application.
2. Requests per second are sent to the web server.
3. Read/write ratio in the database.
4. The number of simultaneously active users in a chat room.

### Example

The book uses Twitter's disclosed information from November 2012 as an example:

Determine their request volume: 

1. posting tweets (averaging 4.6k requests/second, peaking over 12k requests/second), 
2. viewing others' tweets (300k requests/second).

There are two common methods for this: pull and push.

- **Pull**: When a user views their home feed stream, the system retrieves tweets from all users they follow from the database, merges them, and then presents the combined feed.
    
    ![Screen Shot 2023-04-03 at 2.20.19 PM.png](Chapter%201%20Reliable,%20Scalable,%20and%20Maintainable%20App%20c31019aeccb641a191e21cbe9eec1ba3/Screen_Shot_2023-04-03_at_2.20.19_PM.png)
    
    ```sql
    SELECT tweets.*, users.*
      FROM tweets
      JOIN users   ON tweets.sender_id = users.id
      JOIN follows ON follows.followee_id = users.id
      WHERE follows.follower_id = current_user
    ```
    
- **Push**: A feed stream view is maintained for each user. When a user posts a tweet, it is inserted into the feed stream view of all their followers.
    
    ![Screen Shot 2023-04-03 at 2.45.13 PM.png](Chapter%201%20Reliable,%20Scalable,%20and%20Maintainable%20App%20c31019aeccb641a191e21cbe9eec1ba3/Screen_Shot_2023-04-03_at_2.45.13_PM.png)
    
    Maintain a cache for each user's home timeline, like an inbox for each user's tweets. When a user posts a tweet, find all the users who follow them and insert the new tweet into each of their home timeline caches. As a result, the request overhead for reading home timelines is minimal, as the results have already been precomputed.
    
    Twitter's first version used method 1, but the system struggled to keep up with the load of home timeline queries. As a result, the company switched to method 2, which performed better because the frequency of posting tweets was almost two orders of magnitude lower than the frequency of querying home timelines. In this case, it's better to do more work during writing and less work during reading.
    
    However, the downside of method 2 is that posting a tweet now requires a significant amount of additional work. On average, a tweet is sent to about 75 followers, so the 4.6k tweets written per second turn into 345k writes per second to the home timeline caches. But this average value hides the reality that the number of followers varies greatly among users, with some having over 30 million followers. This means that a single tweet could potentially result in 30 million writes to the home timeline cache! Completing such an operation in a timely manner is a huge challenge - Twitter aims to deliver tweets to followers within 5 seconds.
    

Twitter's first version used method 1, but the system struggled to keep up with the load of home timeline queries. As a result, the company switched to method 2, which performed better because **the frequency of posting tweets was almost two orders of magnitude lower than the frequency of querying home timelines.** In this case, it's better to do more work during writing and less work during reading.

However, the downside of method 2 is that posting a tweet now requires a significant amount of additional work. On average, a tweet is sent to about 75 followers, so the 4.6k tweets written per second turn into 345k writes per second to the home timeline caches. But this average value hides the reality that the number of followers varies greatly among users, with some having over 30 million followers. This means that a single tweet could potentially result in 30 million writes to the home timeline cache! Completing such an operation in a timely manner is a huge challenge - Twitter aims to deliver tweets to followers within 5 seconds.

### Describing Performance

- Throughput: The amount of data processed per second, usually denoted as QPS (queries per second).
- Response time: The time observed from the user side between sending a request and receiving a response.
- Latency: In everyday usage, latency is often used interchangeably with response time.
    - Networking, transmission time
    - TTFB (Time to first byte)

Even when repeatedly sending the same request, the response time for each instance may vary slightly. In real-world systems that handle a wide variety of requests, the response times can differ significantly. Therefore, we need to consider the response time as a measurable value distribution, rather than as a single value.

![fig1-4.png](Chapter%201%20Reliable,%20Scalable,%20and%20Maintainable%20App%20c31019aeccb641a191e21cbe9eec1ba3/fig1-4.png)

![Screen Shot 2023-04-03 at 8.07.58 PM.png](Chapter%201%20Reliable,%20Scalable,%20and%20Maintainable%20App%20c31019aeccb641a191e21cbe9eec1ba3/Screen_Shot_2023-04-03_at_8.07.58_PM.png)

### Addressing Load

- Vertical scaling (**scaling up**): This involves using more powerful machines to handle the increased load. For example, using large-scale machines for machine learning training.
- Horizontal scaling (**scaling out**): This approach involves using multiple cheaper machines in parallel to distribute the load. For example, Elon Musk's approach to building rockets.

Both vertical and horizontal scaling have their advantages and drawbacks. Vertical scaling can be limited by the maximum capacity of a single machine, while horizontal scaling can be more complex to manage due to the increased number of machines and the need for efficient load distribution.

There are two types of services:

1. Stateless services: These are relatively simple to scale. Multiple machines can be used, with a gateway or load balancer at the outer layer to distribute incoming requests evenly across the machines. ex: APIs. 
2. Stateful services: Scaling these services requires more careful consideration of factors such as read/write load, storage capacity, data complexity, response time, and access patterns. A suitable architecture should be designed to meet the specific requirements and trade-offs of the given scenario. ex: Database operations. 

## Maintainability

At the beginning of the design process, it's important to consider ways to minimize pain during the maintenance phase, thus avoiding your software system becoming a legacy system. To achieve this, we will focus on three design principles:

1. Operability: Make it easy for the operations team to take over painlessly. The software should be designed in a way that allows for easy troubleshooting, monitoring, and maintenance.
2. Simplicity: Facilitate smooth onboarding for new developers. This requires a reasonable abstraction and minimizing various complexities. For example, employing hierarchical abstraction helps manage complexity and makes it easier for new developers to understand the system.
3. Evolvability: Enable rapid adaptation to future requirements. Avoid overly tight coupling and binding the code to specific implementations. This is also referred to as extensibility, modifiability, or plasticity. Designing the system to be flexible and adaptable allows for easier changes and upgrades as requirements evolve over time.

By following these principles, you can ensure that the software is more maintainable, easier for new developers to work with, and adaptable to changing requirements. This ultimately leads to a more sustainable and efficient development process.

### Operability

Effective operation and maintenance is undoubtedly a highly skilled task:

1. Closely monitor system status and quickly recover when problems arise.
2. After recovery, review the issue, and identify the root cause.
3. Regularly update and upgrade platforms, libraries, and components.
4. Understand the relationships between components to avoid cascading failures.
5. Establish automated configuration management, service management, and update/upgrade mechanisms.
6. Perform complex maintenance tasks, such as moving a storage system from one data center to another.
7. Ensure system security during configuration changes.

Good maintainability of a system means that well-defined maintenance processes are documented and automated, freeing up human resources to focus on higher-value tasks:

1. User-friendly documentation and consistent operation standards.
2. Detailed monitoring dashboards, self-checks, and alerts.
3. Generic default configurations.
4. Self-healing mechanisms when problems arise, with the option for manual intervention by administrators if necessary.
5. Automate maintenance processes as much as possible.
6. Avoid single points of dependency, whether it's machines or people.

By focusing on these aspects, you can create a software system that is easier to maintain and operate, making it more sustainable and efficient throughout its lifecycle.