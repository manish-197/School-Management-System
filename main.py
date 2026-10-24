import json
from abc import ABC, abstractmethod
from pathlib import Path

database = "school_data.json" # main database file
data = {"students" : [], "teachers": []} #copy database

if Path(database).exists():
    with open(database, 'r') as f:
        content = f.read()
        if content:
            data = json.loads(content)

def save():
    with open(database, 'w') as f:
        json.dump(data, f, indent=4)


class Persons(ABC):
    @abstractmethod
    def get_roles(self):
        pass

    @abstractmethod
    def register(self):
        pass

    @abstractmethod
    def show_details(self):
        pass

    @staticmethod
    def validate_email(email):
        if '@' in email and '.' in email:
            return True
        else:
            return False


class Student(Persons):
    def get_roles(self):
        return "Student"

    def register(self):
        name = input('Enter student name: ')
        age = int(input('Enter student age: '))
        email = input('Enter student email: ')
        roll_no = input('Enter student roll number: ')

        if not Persons.validate_email(email):
            print('Invalid email format')
            return
        
        for i in data['students']:
            if i['roll_no'] == roll_no:
                print('Student with this roll number already exists')
                return

        data['students'].append({
            'name': name,
            'age': age,
            'email': email,
            'roll_no': roll_no,
            'grades': {}
        })

        save()
        print(f'Student {name} registered successfully!')

    def show_details(self):
        roll_no = input('Enter student roll number: ')
        for i in data['students']:
            if i['roll_no'] == roll_no:
                grades = i['grades']
                avg = sum(grades.values()) / len(grades) if grades else 0

                print(f' \n Student Details:')
                print(f'Name: {i["name"]}')
                print(f'Age: {i["age"]}')
                print(f'Email: {i["email"]}')
                print(f'Roll Number: {i["roll_no"]}')
                print(f'Grades: {grades}')
                print(f'Average Marks: {avg}')
                return
            else:
                print('Student with this roll number does not exist')

    def add_grades(self):
        roll_no = input('Enter student roll number: ')
        subject = input('Enter subject: ')
        marks = float(input('Enter marks: '))
        for i in data['students']:
            if i['roll_no'] == roll_no:
                i['grades'][subject] = marks
                save()
                print(f'Grades added for student with roll number {roll_no}')
                return
            else:
                print('Student with this roll number does not exist')


class Teacher(Persons):
    def get_roles(self):
        return 'Teacher'

    def register(self):
        name = input('Enter teacher name: ')
        age = int(input('Enter teacher age: '))
        email = input('Enter teacher email: ')
        subject = input('Enter teacher subject: ')
        employee_id = input('Enter teacher employee ID: ')
        
        if not Persons.validate_email(email):
            print('Invalid email format')
            return

        for i in data['teachers']:
            if i['employee_id'] == employee_id:
                print('Teacher with this employee ID already exists')
                return

        data['teachers'].append({
            'name': name,
            'age': age,
            'email': email,
            'subject': subject,
            'employee_id': employee_id
        })

        save()
        print(f'Teacher {name} registered successfully!')

    def show_details(self):
        employee_id = input('Enter teacher employee ID: ')
        for i in data['teachers']:
            if i['employee_id'] == employee_id:
                print(f' \n Teacher Details:')
                print(f'Name: {i["name"]}')
                print(f'Age: {i["age"]}')
                print(f'Email: {i["email"]}')
                print(f'Subject: {i["subject"]}')
                print(f'Employee ID: {i["employee_id"]}')
                return
            else:
                print('Teacher with this employee ID does not exist')

teacher = Teacher()
student = Student()

print('press 1 to register a student')
print('press 2 to register a teacher')
print('press 3 to add grades')
print('press 4 to show a student details')
print('press 5 to show a teacher details')

choice = int(input('Enter your choice: '))

if choice == 1:
    student.register()
elif choice == 2:
    teacher.register()
elif choice == 3:
    student.add_grades()
elif choice == 4:
    student.show_details()
elif choice == 5:
    teacher.show_details()
else:
    print('Invalid choice')
