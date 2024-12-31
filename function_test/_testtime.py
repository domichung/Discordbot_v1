import time
#next_load_time = '2024-11-14-20:00:00'
#now_time = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())

import datetime
a = datetime.datetime(100,1,1,11,34,59)
b = a + datetime.timedelta(0,3) # days, seconds, then other fields.
print(a.time())
print(b.time())

#print(next_load_time)
#print(now_time)
#print(next_load_time<now_time)