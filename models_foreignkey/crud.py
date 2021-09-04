# crud.py
from model import db, Employee, Project, Company


# Employeeからの紐づけ
# 全件select
# for e in Employee.query.all():
#     print('e: ', e.projects[0].name)  # Employee name = John, company is Microsoft
#     print('e: ', e.company.name)  # Microsoft

# Employee先頭1件select
# e = Employee.query.first()
# print(e)
# print(e.company.name)  # John
# print(e.projects[1].name)  # Excel Project
# for project in e.projects:
#     print(project.name)

# Projectからの紐づけ
# print('*' * 100)
# p = Project.query.get(1)  # Word Project -> John
# print(p.employees.name)  # John

# Companyからの紐づけ
# c = Company.query.get(1)  # Microsoft -> John
# print(c.employees.name)  # John

# 紐づけ方法の違い
e = Employee.query.first()
print(type(e.projects))
print(e.projects.order_by(Project.id.desc()).limit(1).first().name)  # model.pyでprojectsにlazy='dynamic'を指定
