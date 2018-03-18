# comment-analyzer
Script to gather some simple statistic on the comment sections of news articles

# Usage Example
```
./twenty_minutes.py ./twenty_minutes.py http://www.20min.ch/sport/tennis/story/Federers--Armdruecken--mit-Del-Potro-in-der-Wueste-31589649
```
The resulting SQLite file ```twenty_minutes.sqlite3``` can be analyzed using e.g. [SQLite Database Browser](http://sqlitebrowser.org/).

# Example Analysis
## Query for the Top 10 Commenters
```sql
SELECT
	author,
	max(vote_up) vote_up_max,
	min(vote_up) vote_up_min,
	avg(vote_up) vote_up_average,
	sum(vote_up) vote_up_total,
	count(*) comment_count
FROM comment JOIN article ON comment.article_id = article.id
WHERE article.id = '31589649'
GROUP BY author
ORDER BY comment.vote_up DESC
LIMIT 10
```

## Result
author|vote_up_max|vote_up_min|vote_up_average|vote_up_total|comment_count
----- | --------- | --------- | ------------- | ----------- | ---------- |
Waterpolo1s|93|93|93.0|93|1
Dave Müller|25|25|25.0|25|1
Tennisfan|24|24|24.0|24|1
Menscheit|19|19|19.0|19|1
Benny|17|16|16.5|33|2
S.k.aus n|16|16|16.0|16|1
Susanne |15|15|15.0|15|1
Szenenkenner|15|15|15.0|15|1
Hugo Boss|11|11|11.0|11|1
Lisa|11|11|11.0|11|1
