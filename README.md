# take-grant.can-share

Efficient implementation of an algorithm for 𝑐𝑎𝑛_𝑠ℎ𝑎𝑟𝑒 verification predicate in Take-Grant protection model.<br>
Written in Python with help of NetworkX lib.<br>
Linear computation complexity based on the L. Snyder algorithm, parallelism, tests, benchmarks.<br>
<br>
[Article on the work done](https://github.com/lifantev/take-grant/blob/master/take_grant_can_share_impl_article.pdf).

Template to run from command-line:
```  
python3 can_share.py -f <filename_of_protection_graph.json> -s <source_object> -d <destination_object> -l <rule_label>
```
