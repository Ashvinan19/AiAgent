from functions.run_python_file import run_python_file


print("main.py:")
print(run_python_file("calculator", "main.py"))

print("\nmain.py with args:")
print(run_python_file("calculator", "main.py", ["3 + 5"]))

print("\ntests.py:")
print(run_python_file("calculator", "tests.py"))

print("\n../main.py:")
print(run_python_file("calculator", "../main.py"))

print("\nnonexistent.py:")
print(run_python_file("calculator", "nonexistent.py"))

print("\nlorem.txt:")
print(run_python_file("calculator", "lorem.txt"))
