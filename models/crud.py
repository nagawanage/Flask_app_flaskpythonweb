from model import db, Person

db.create_all()
man1 = Person('Taro', 18)
man2 = Person('Jiro', 19)
man3 = Person('Saburo', 20)

print(man1, man2, man3)
db.session.add(man1)
db.session.add_all([man2, man3])
db.session.commit()
print(man1, man2, man3)
