# crud.py

from model import db, Person
from datetime import datetime

man1 = Person(
    'Taro',
    '090-2222-2222',
    21,
    datetime.now(),
    datetime.now()
)
man2 = Person(
    'Jiro',
    '090-4444-4444',
    22,
    datetime.now(),
    datetime.now()
)
man3 = Person(
    'Saburo',
    '090-3333-3333',
    23,
    datetime.now(),
    datetime.now()
)

db.session.add_all([man1, man2, man3])
db.session.commit()
