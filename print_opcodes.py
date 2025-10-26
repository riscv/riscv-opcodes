# Import the 'os' module, which provides functions to interact with the operating system
# We need this to work with files and directories
import os

# Create an empty list to store all instruction names we find
# A list in Python is like an array - it can hold multiple items
instructions = []

# Store the directory path as a string variable
# This is the folder where all the instruction definition files are located
extensions_dir = 'extensions'

def process_dir(directory):
    # Loop through every item (file or folder) in the given directory
    # os.listdir() returns a list of all names in the directory
    for filename in os.listdir(directory):
        
        # Create the full path by joining directory path and filename
        # Example: 'extensions' + 'rv_i' becomes 'extensions/rv_i'
        filepath = os.path.join(directory, filename)
        
        # Check if this path is a directory (folder) using os.path.isdir()
        # Returns True if it's a folder, False if it's a file
        if os.path.isdir(filepath):
            # If it's a folder, call this same function again (recursion)
            # This allows us to process subdirectories like 'extensions/unratified/'
            process_dir(filepath)
        
        # If the previous 'if' was False
        # Check if the filename starts with 'rv' (all RISC-V files start with 'rv')
        elif filename.startswith('rv'):
            
            # Open the file for reading ('r' means read mode)
            # 'with' ensures the file is properly closed after we're done
            # 'as file' creates a variable 'file' that represents the opened file
            with open(filepath, 'r') as file:
                
                # Loop through each line in the file, one at a time
                for line in file:
                    
                    # Remove whitespace (spaces, tabs, newlines) from both ends of the line
                    # Example: "  add  \n" becomes "add"
                    line = line.strip()
                    
                    # Check three conditions using 'and':
                    # 1. 'line' - checks if the line is not empty (empty strings are False in Python)
                    # 2. 'not line.startswith('#')' - makes sure line doesn't start with # (comments)
                    # 3. 'not line.startswith('$')' - skip special keywords like $import, $pseudo_op
                    if line and not line.startswith('#') and not line.startswith('$'):
                        
                        # Split the line into words (by spaces) and take the first word [0]
                        # Example: "add rd rs1 rs2 ..." becomes ["add", "rd", "rs1", ...]
                        # [0] gets the first element, which is the instruction name
                        name = line.split()[0]
                        
                        # Add this instruction name to our list
                        # append() adds an item to the end of the list
                        instructions.append(name)

# Call the function to start processing from the 'extensions' directory
process_dir(extensions_dir)

# Remove duplicates and sort alphabetically:
# 1. set(instructions) - converts list to a set, which automatically removes duplicates
#    Example: ['add', 'sub', 'add'] becomes {'add', 'sub'}
# 2. sorted() - sorts the set alphabetically and converts it back to a list
#    Example: {'sub', 'add'} becomes ['add', 'sub']
instructions = sorted(set(instructions))

# Open a new file called 'all_opcodes.txt' for writing ('w' means write mode)
# If the file exists, it will be overwritten; if not, it will be created
# 'as outfile' creates a variable to represent this file
with open('all_opcodes.txt', 'w') as outfile:
    
    # Loop through each instruction in our sorted list
    for instr in instructions:
        
        # Write the instruction name to the file, followed by a newline character '\n'
        # This puts each instruction on its own line in the file
        outfile.write(instr + '\n')

# f"..." is an f-string - it allows us to insert variables directly into the string
# len(instructions) counts how many items are in the list
print(f"Total unique instructions: {len(instructions)}")