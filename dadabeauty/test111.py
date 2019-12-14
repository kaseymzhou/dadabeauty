import redis
import json
r = redis.Redis(host='127.0.0.1',port=6379,db=7)

# r.zadd('product_like',{'01':0})
# r.zadd('product_like',{'02':1})
# r.zadd('product_like',{'03':2})
# r.zadd('product_like',{'04':3})


# rank = r.zrevrange('product_like',0,-1,withscores=True)
# rank_list = rank[:3]
# new_rank_list = []
# for item in rank_list:
#     item = list(item)
#     item[0] = item[0].decode()
#     new_rank_list.append(item)
#
# print(new_rank_list)

r.set('index_cache',"{'a':1}")
r.set('index_cache',"{'a':2}")
print(r.get('index_cache'))

r.set("name","zhangsan")
print(r.get("name"))