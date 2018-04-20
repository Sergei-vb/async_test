#!/usr/bin/env python3


class QuerySet:
    def __init__(self, data=None):
        self.collect = []
        self.data = data

    def __repr__(self):
        if self.data is None:
            return "<QuerySet [<UserImage: UserImage>]>"
        else:
            return "<QuerySet {0}>".format(self.data)

    def append(self, obj):
        self.collect.append(obj)

    def values(self):
        return QuerySet(self.collect)

    def exclude(self, tag=None):
        self.collect = [i for i in self.data if i["tag"] != tag]
        return QuerySet(self.collect)


class Database:
    collect = []

    def __init__(self, data):
        self.collect.append(data)


class Objects:

    @staticmethod
    def all():
        return Database.collect

    @staticmethod
    def filter(tag=None, user_id=None):
        key = "tag" if tag else "user_id" if user_id else None
        val = tag if tag else user_id if user_id else None
        if key:
            answer = QuerySet()
            for obj in Database.collect:
                if obj[key] == val:
                    answer.append(obj)
            if answer.collect:
                return answer


class UserImage:
    objects = Objects()

    def __init__(self, user_id, image_id, tag, created, size):
        self.user_id = user_id
        self.image_id = image_id
        self.tag = tag
        self.created = created
        self.size = size

    def save(self):
        inst = dict(user_id=self.user_id,
                    image_id=self.image_id,
                    tag=self.tag,
                    created=self.created,
                    size=self.size)
        Database(inst)
