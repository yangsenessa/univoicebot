# coding: utf8

"""Delay Queue"""

import json
import time
import uuid

import redis


class DelayQueue(object):

    """延迟队列"""

    QUEUE_KEY = 'delay_queue'
    DATA_PREFIX = 'queue_data'
    conf= dict()

    def __init__(self, conf):
        host, port, db, passwd = conf['host'], conf['port'], conf['db'], conf['passwd']
        self.client = redis.Redis(host=host, port=port, db=db,password=passwd)

    def push(self, data,task_sec):
        """push

        :param data: data
        """
        # 唯一ID
        task_id = str(uuid.uuid4())
        data_key = '{}_{}'.format(self.DATA_PREFIX, task_id)
        # save string
        self.client.set(data_key, data)
        # add zset(queue_key=>data_key,ts)
        self.client.zadd(self.QUEUE_KEY, data_key, int(task_sec))
        
    def pop(self, num=500, previous=3):
        """pop多条数据

        :param num: pop多少个
        :param previous: 获取多少秒前push的数据
        """
        # 取出previous秒之前push的数据
        until_ts = int(time.time()) - previous
        task_ids = self.client.zrangebyscore(
            self.QUEUE_KEY, 0, until_ts, start=0, num=num)
        if not task_ids:
            return []

        # 利用删除的原子性,防止并发获取重复数据
        pipe = self.client.pipeline()
        for task_id in task_ids:
            pipe.zrem(self.QUEUE_KEY, task_id)
        data_keys = [
            data_key
            for data_key, flag in zip(task_ids, pipe.execute())
            if flag
        ]
        if not data_keys:
            return []
        # load data
        data = [
            json.loads(item)
            for item in self.client.mget(data_keys)
        ]
        # delete string key
        self.client.delete(*data_keys)
        return data