# -*-coding: utf-8


class Teacher:
    def __init__(self, name, sex, age):
        self.name = name
        self.sex = sex
        self.age = age
        self.list_student = []

    def get_name(self):
        return self.name

    def get_sex(self):
        return self.sex

    def get_age(self):
        return self.age

    def add_student(self, student):
        self.list_student.append(student)

    def get_student(self):
        return self.list_student


class Student:
    def __init__(self, name, sex, age):
        self.name = name
        self.sex = sex
        self.age = age

    def get_name(self):
        return self.name

    def get_sex(self):
        return self.sex

    def get_age(self):
        return self.age

    def set_teacher(self, teacher):
        self.teacher = teacher

    def get_teacher(self):
        return [self.teacher.get_name(), self.teacher.get_sex(), self.teacher.get_age()]

    def print_info(self):
        print('name:', self.name, 'sex:', self.sex, 'age:', self.age)
        return -6


class Classes:
    def __init__(self, teacher, student):
        self.teacher = teacher
        self.student = student

    def get_teacher(self):
        return [self.teacher.get_name(), self.teacher.get_sex(), self.teacher.get_age()]

    def get_student(self):
        return [self.student.get_name(), self.student.get_sex(), self.student.get_age()]


t1 = Teacher('ypf', 'boy', 27)
s1 = Student('ywy', 'boy', 29)
s2 = Student('yjx', 'boy', 27)
t1.add_student(s1)
t1.add_student(s2)
l_student = t1.get_student()
for i in l_student:
    i.print_info()

# print('t1.get_student()', t1.get_student())
# s1.set_teacher(t1)
# print('s1.get_teacher()', s1.get_teacher())
# c1 = Classes(t1, s1)
# print('c1.get_teacher()', c1.get_teacher())
# print('c1.get_student()', c1.get_student())

