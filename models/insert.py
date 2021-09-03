from model import db, Person
from datetime import datetime

man1 = Person(
    # 'Taro',
    None,  # nanashi
    '090-1111-2222',
    12,
    datetime.now(),
    datetime.now()
)
db.session.add(man1)
db.session.commit()
