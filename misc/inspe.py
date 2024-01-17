import dis

def inspect_bytecode(file_path):
    with open(file_path, 'rb') as file:
        code = compile(file.read(), file_path, 'exec')

    instructions = list(dis.get_instructions(code))
    
    current_line = None

    for instruction in instructions:
        if current_line is None or current_line != instruction.starts_line:
            current_line = instruction.starts_line
            print(f"\nLine {current_line}:")

        print(f"    {instruction.opname} {instruction.argrepr}")


# Replace 'your_file.py' with the path to your Python file
inspect_bytecode('test.py')
