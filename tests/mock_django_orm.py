#!/usr/bin/env python3
"""Mock Django ORM."""


class QuerySet:
    """Imitates work with queryset after filter."""
    def __init__(self, data=None):
        self.collect = data if data else []

    def __iter__(self):
        return iter(self.collect)

    def append(self, obj):
        """Adds object to queryset."""
        self.collect.append(obj)

    def values(self):
        """Ensures that code works correctly."""
        return QuerySet(self.collect)

    def exclude(self, tag=None):
        """Excludes objects from queryset."""
        self.collect = [i for i in self.collect if i["tag"] != tag]
        return QuerySet(self.collect)


# pylint: disable=too-few-public-methods
class Database:
    """Stores data."""
    collect = []

    def __init__(self, data):
        self.collect.append(data)


class Objects:
    """Provides access to objects."""

    @staticmethod
    def all():
        """Gives objects all."""
        return Database.collect

    @staticmethod
    def filter(tag=None, user_id=None):
        """Gives objects filter."""
        key = "tag" if tag else "user_id" if user_id else None
        val = tag if tag else user_id if user_id else None
        answer = QuerySet()
        if key:
            for obj in Database.collect:
                if obj[key] == val:
                    answer.append(obj)
        return answer


# pylint: disable=too-few-public-methods
class UserImage:
    """Creates Model."""
    objects = Objects()

    def __init__(self, **kwargs):
        self.user_id = kwargs["user_id"]
        self.image_id = kwargs["image_id"]
        self.tag = kwargs["tag"]
        self.created = kwargs["created"]
        self.size = kwargs["size"]

    def save(self):
        """Saves model."""
        inst = dict(user_id=self.user_id,
                    image_id=self.image_id,
                    tag=self.tag,
                    created=self.created,
                    size=self.size)
        Database(inst)
