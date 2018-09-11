import platform
import uuid

from peewee import Model, MySQLDatabase, Field, CharField, DateTimeField, TextField, BooleanField, SQL
from redis import Redis

CATEGORY_TO_INDEX = {
    '玄幻修真': 0,
    '科幻网游': 1,
    '都市重生': 2,
    '架空历史': 3,
    '武侠世界': 4,
    '灵异悬疑': 5,
}

INDEX_TO_CATEGORY = {
    0: '玄幻修真',
    1: '科幻网游',
    2: '都市重生',
    3: '架空历史',
    4: '武侠世界',
    5: '灵异悬疑',
}

if platform.system() == 'Darwin':
    MySQL_DB = MySQLDatabase(
        host='127.0.0.1',
        port=3306,
        user='root',
        database='lulu-novel'
    )


class ModelBase(Model):
    class Meta:
        database = MySQL_DB


class TinyInt(Field):
    field_type = 'TINYINT'


class Book(ModelBase):
    bid = CharField(max_length=32, default=uuid.uuid1().hex)
    title = CharField(max_length=64)
    author = CharField(max_length=32)
    category_index = TinyInt()
    updateTime = DateTimeField(formats='%Y-%m-%d %H:%M:%S',
                               constraints=[SQL('DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')])
    end = BooleanField(default=False)
    latestChapterName = CharField(max_length=128)
    latestChapterCid = CharField(max_length=32)
    firstChapterName = CharField(max_length=128)
    firstChapterCid = CharField(max_length=32)

    # 内部做了个编码准换
    @property
    def category(self):
        return INDEX_TO_CATEGORY[self.category_index]

    @category.setter
    def category(self, category):
        self.category_index = CATEGORY_TO_INDEX[category]

    class Meta:
        indexes = (
            (('bid', 'title', 'author'), False),
            (('category_index',), False)
        )


class Chapter(ModelBase):
    bid = CharField(max_length=32)
    cid = CharField(max_length=32, default=uuid.uuid1().hex)
    context = TextField(null=True)
    collectedTime = DateTimeField(formats='%Y-%m-%d %H:%M:%S',
                                  constraints=[SQL('DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')])

    class Meta:
        indexes = (
            (('cid', 'bid'), True),
        )


if __name__ == '__main__':
    # MySQL_DB.create_tables([Book, Chapter])
    # MySQL_DB.drop_tables([Book, Chapter])
    print(*MySQL_DB.execute_sql('show tables'))
