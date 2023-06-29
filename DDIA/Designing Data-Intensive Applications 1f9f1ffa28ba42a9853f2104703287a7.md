# Designing Data-Intensive Applications

<aside>
💡 **Notion Tip:** Use this page to keep track of all your notes and highlights. You can also reference other Notion pages by typing the `[[` command. Learn more [here](https://www.notion.so/help/create-links-and-backlinks).

</aside>

![Untitled](Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Untitled.png)

**Table of contents**

[English version](https://public.nikhil.io/Designing%20Data%20Intensive%20Applications.pdf)

[中文版](https://github.com/Vonng/ddia/blob/master/zh-tw/README.md)

## Shift Table

- PartII. Distributed Data (Week 10~20)
    
    
    | Week (Date) | Note | 乙陞 | 力維 | 凱唯 | 昱豪 | 子杰 | 呈毅 |
    | --- | --- | --- | --- | --- | --- | --- | --- |
    | Week 10 (6/6) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60.md- Leaders and Followers  |  |  | ● |  |  |  |
    | Week 11 (6/13) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60.md- Problems with Replication Lag |  |  |  | ● |  |  |
    | Week 12 (6/20) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60.md- Handling Write Conflicts |  |  |  |  | ●  |  |
    | Week 13 (6/27) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60.md- Quorums for reading and writing |  |  |  |  |  | ●  |
    | Week 14 (7/4) | Chapter 6 | ● |  |  |  |  |  |
- Part I. Foundations of Data Systems
    
    
    | Week (Date) | Note | 乙陞 | 力維 | 凱唯 | 奕智 | 昱豪 | 子杰 | 呈毅 |
    | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    | Week 1 (4/4) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%201%20Reliable,%20Scalable,%20and%20Maintainable%20App%20c31019aeccb641a191e21cbe9eec1ba3.md | ● |  |  |  |  |  |  |
    | Week 2 (4/11) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195.md |  | ● |  |  |  |  |  |
    | Week 3 (4/18) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195.md |  |  | ● |  |  |  |  |
    | Week 4 (4/25) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848.md |  |  |  | ● |  |  |  |
    | Week 5 (5/2) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848.md |  |  |  |  | ● |  |  |
    | Week 6 (5/9) | TODO |  |  |  |  |  |  |  |
    | Week 7 (5/16) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa.md |  |  |  |  |  | ● |  |
    | Week 8 (5/23) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa.md Avro | ● |  |  |  |  |  |  |
    | Week 9 (5/30) | Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa.md Message queue 
    Part II. Distributed Data (Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Part%20II%20Distributed%20Data%20b79959a87cb7446fa708416f6ba8fbaf.md)  |  | ● |  |  |  |  |  |

## Notes

[Chapter 1. Reliable, Scalable, and Maintainable Applications](Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%201%20Reliable,%20Scalable,%20and%20Maintainable%20App%20c31019aeccb641a191e21cbe9eec1ba3.md)

[Chapter 2. Data Models and Query Language](Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%202%20Data%20Models%20and%20Query%20Language%20a2cb277a89444ef4a989ac7da0878195.md) 

[Chapter 3. Storage and Retrieval](Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%203%20Storage%20and%20Retrieval%2044d1e0a504124ccdae0787b8ae159848.md) 

[Chapter 4. **Encoding and Evolution**](Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%204%20Encoding%20and%20Evolution%20309722a0df8647ba97b1c668c6a476fa.md) 

[Part II. Distributed Data](Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Part%20II%20Distributed%20Data%20b79959a87cb7446fa708416f6ba8fbaf.md)

[Chapter 5. Replication](Designing%20Data-Intensive%20Applications%201f9f1ffa28ba42a9853f2104703287a7/Chapter%205%20Replication%20e2c04b0d567d4f6db10bc5aed2df5e60.md)

## Key takeaways

- 

## Quotes

> 
> 

## Summary

-