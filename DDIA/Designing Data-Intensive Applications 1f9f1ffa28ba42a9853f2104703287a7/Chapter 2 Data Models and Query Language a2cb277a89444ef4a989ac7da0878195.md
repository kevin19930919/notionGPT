# Chapter 2. Data Models and Query Language

## Summary

- Discussed various data models and its historical evolution.
- Compare the relational model,  the document models, and a few graph-based data models.
- not only on how the software is written, but also on how we *think about the problem* that we are solving

## Relational Model vs. Document Model

- SQL
- Relational database are built for business data processes.
    - The goal of the relational model was to hide that implementation detail behind a cleaner interface.
    - Transaction processing
    - batch processing
- NoSQL - Not only sql
    - Not actually refer to particular tech, basically open source, distributed, non-relational database.
    - Greater scalability (distributed), free from restrictions of RDBMS schemas and operations. (?)
- The Object-Relational Mismatch ([explanation](https://medium.com/mingjen/%E9%97%9C%E6%96%BC%E7%89%A9%E4%BB%B6%E5%92%8C%E9%97%9C%E8%81%AF%E8%B3%87%E6%96%99%E5%BA%AB-rdbms-%E7%9A%84%E9%98%BB%E6%8A%97%E4%B8%8D%E5%8D%80%E9%85%8D-impedance-mismatch-edbbd009be12))
    - ORM (Object-Relational Mapping) model is usually used for mapping DB data and application layer. But in some cases, the table schema (relational model) might be disconnected with the application code (OOP) → impedance mismatch
    - Solutions are:
        1. 1 to many model, put a foreign reference to the main table. 
            
            ![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled.png)
            
        2. RDBMS are supporting XML or JSON datatype.
        3. Document model: XML or JSON 
            
            ![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%201.png)
            
            ![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%202.png)
            
- Many-to-One and Many-to-Many Relationships
    - Documents models works well for 1-many relationship, but made many-many difficult if not supporting joins.
- relational vs. document databases
    - **document data model**: schema flexibility, better performance (denormalize, locality), data structure closer to applications.
    - **relational data model**: better support for join, many-many & many-1 relationships.
- Things to consider between those 2:
    - Which one leads to simpler application code?
        - Retrieving data relationships: many-many, many-1 or 1-many
    - Is Schema flexibility necessary?
        - schema changes:
            - schema-on-read (document model): Having code in application to handle the changes
        - schema-on-write (RDBMS):
            - Need `ALTER`, `UPDATE` to handle the changes that might cause downtime.
                
                (If that is unacceptable, the application can leave first_name set to its default of NULL and fill it in at read time, like it would with a document database.)
                
            - Useful mechanism for documenting and enforcing that structure.

## Query Languages for Data

- declarative query language (ex: SQL)
    - more concise, abstraction layer to the database engine implementation, parallel execution
    - Call back with [CH1](Chapter%201%20Reliable,%20Scalable,%20and%20Maintainable%20App%20c31019aeccb641a191e21cbe9eec1ba3.md)
- imperative code (ex: IMS, CODASYL)

### Declarative Queries on Web (browser)

An web browser example to compare declarative and imperative approaches

- declarative way: CSS, XSL
    
    ![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%203.png)
    
- imperative way: Javascript
    
    ![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%204.png)
    

|  | declarative | imperative |
| --- | --- | --- |
| Focus | Declarative languages emphasize the description of the desired outcome or result, rather than the step-by-step process to achieve that result. | Imperative languages describe the step-by-step process to achieve a specific result, focusing on the sequence of actions and the state changes they produce. |
| Abstraction | These languages tend to have a higher level of abstraction, allowing programmers to express their intentions more concisely | These languages tend to have a lower level of abstraction, requiring more explicit instructions from the programmer. |
| Examples | SQL , Haskell | C, C++, Java, and Python |
| Benefits | Declarative languages can lead to more concise and readable code, and may allow for better optimization by compilers or interpreters. | 1. Imperative languages can provide more control over the execution of code, which can be beneficial in performance-critical applications. |

### Map Reduce

Somewhere between declarative and imperative approaches. functional programming 

- SQL
    
    ```sql
    SELECT 
    	date_trunc('month', observation_timestamp) AS observation_month,
    	sum(num_animals) AS total_animals
    FROM observations
    WHERE family = 'Sharks'
    GROUP BY observation_month
    ;
    ```
    
    1. `FROM`, `WHERE` filter shark family
    2. `GROUP BY`
    3. `SELECT` Add up the number
- MongoDB Map Reduce
    
    Low-level programming model for distributed execution on clusters. They are powerful in terms of parsing string, calling libraries, calculating, etc.  
    
    Problems:
    
    1. cannot perform additional queries and must not have any side effects
    2. Have to write carefully coordinated functions
    
    ```sql
    db.observations.mapReduce(
    	function map() {
    		var year = this.observationTimestamp.getFullYear();
    		var month = this.observationTimestamp.getMonth() + 1;
    		emit(year + "-" + month, this.numAnimals);
    	},
    	function reduce(key, values) {
    		return Array.sum(values);
    	},
    	{
    		query: { family: "Sharks" },
    		out: "monthlySharkReport"
    	}
     );
    ```
    
    1. `query: { family: "Sharks" }`:  Filter to consider when Shark can be specified declaratively (MongoDB feature)
    2. `map()`: Called when filter matched `query`. Emits a key, to group the document values→ key-value pair
    3. For all key-value pairs, `reduce()`is called once to aggregate the value. 
    4. Output written to the collection `out: "monthlySharkReport"`
- `map()` & `reduce()`
    1. Map phase: The input dataset is divided into smaller chunks, which are then processed by the Map function independently and in parallel. The Map function takes a set of input key-value pairs and produces a set of intermediate key-value pairs. The key-value pairs are typically grouped by their keys to prepare for the next phase.
    2. Reduce phase: The intermediate key-value pairs from the Map phase are sorted and grouped by their keys. The Reduce function is then applied to each group of values with the same key. The Reduce function processes these values and generates a set of output key-value pairs, which form the final result of the MapReduce computation.

> A NoSQL system may find itself accidentally reinventing SQL
> 

- [Functional programming](https://mgleon08.github.io/blog/2019/07/26/functional-programming/)
    - **First-class functions**: Functions are treated as values, allowing them to be passed as arguments to other functions, returned as results, or stored in data structures.
    - **Immutability**: Data is typically immutable, meaning once it is created, it cannot be changed. This leads to fewer side effects and makes code more predictable and easier to reason about.
    - **Pure functions**: Functions do not have any side effects, and their output is solely determined by their input. This makes it easier to understand and test the code.
    - **Recursion**: Functional programming often favors recursion over looping constructs for iteration.
    - **Higher-order functions**: These are functions that can take other functions as arguments or return them as results. Examples include **`map`**, **`filter`**, and **`reduce`**.
    - **Lazy evaluation**: Evaluation of expressions can be delayed until their values are needed, which can improve performance in some cases.

## Graph-Like Data Models

**Consider graph data model when many-many relationships are very common in your application.**

**Data Models**: 

property graph, ex: Neo4j, Titan, InfiniteGraph

triple-store model, ex: Datomic, AllegroGraph

**Query Languages**: 

Declarative: Cypher, SPARQL, Datalog

Imperative: Gremlin, (Amazon Neptune) → [https://gremlify.com/](https://gremlify.com/) 

**Graph Processing Framework**: Pregel 

### Property graph (data model)

| Vertex (node) | Edge  |
| --- | --- |
| unique ID | unique ID |
| A set of outgoing edges | Edge start vertex (tail?) |
| A set of incoming edges | Edge end vertex (head?) |
|  | Relationship between start/end vertices  |
| A collection of properties | A collection of properties |
- Great flexibility for data modeling
- Evolvability

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%205.png)

### **Cypher Query Language**

- Declarative query language for property graph
- Created for Neo4j
- Example for representing data

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%206.png)

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%207.png)

- Find the names of whom emigrated from the US to Europe
    
    → find vertices have:
    
    1. `BORN_IN` edge to a location within the US 
    2. `LIVING_IN` edge to a location within Europe 
    
    ![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%208.png)
    
- Compare the same result with SQL data modeling
    - Would be very clumsy in comparison to Cypher
    - *The same query expressed in SQL*
        
        Graph data can be represented in relational databases. However, if the graph data is already stored in a relational structure, can we also query it using SQL?
        
        The answer is yes, but it can be challenging. **In relational databases, you usually know beforehand which joins are needed in the query. In graph queries, you may need to traverse a variable number of edges before finding the vertex you are looking for**, meaning the number of joins is not predetermined.
        
        ![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%209.png)
        
        ![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%2010.png)
        

### Triple-Stores (data model)

- all information is stored in the form of three-part statements: (subject, predicate, object)

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%206.png)

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%2011.png)

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%2012.png)

### SPARQL (query language)

- short for “SPARQL Protocol and RDF Query Language”
- Earlier than Cypher

Cypher

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%208.png)

SPARQL

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%2013.png)

### Datalog (OG of graph query language)

- Query language of Datomic and Cascalog (query large dataset in Hadoop)
- Similar data model to triple-store
    
    
    | Triple-Store | Datalog |
    | --- | --- |
    | (subject, predicate, object) | predicate(subject, object) |

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%206.png)

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%2014.png)

![Untitled](Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195/Untitled%2015.png)