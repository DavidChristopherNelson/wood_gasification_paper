import subprocess
import os

def open_numbers_file(spreadsheet_name):
    applescript = f'''
        tell application "Numbers"
            open "{os.path.abspath(spreadsheet_name)}.numbers"
        end tell
        '''
    process = subprocess.Popen(['osascript', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    stdout, stderr = process.communicate(applescript)

    if stderr:
        raise Exception(f"AppleScript Error: {stderr}")

    return stdout

def close_numbers_file():
    applescript = f'''
        tell application "Numbers"
            close front document saving yes
        end tell
    '''

    process = subprocess.Popen(['osascript', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    process.communicate(applescript)

def read_cell_value(sheet_name, table_name, cell):
    applescript = f'''
        tell application "Numbers"
            tell sheet "{sheet_name}" of front document
                tell table "{table_name}"
                    set cellValue to value of cell "{cell}"
                end tell
            end tell
        end tell
        return cellValue
        '''

    process = subprocess.Popen(['osascript', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    stdout, stderr = process.communicate(applescript)

    if stderr:
        raise Exception(f"AppleScript Error: {stderr}")
    return stdout.strip()

def write_to_cell_in_numbers(sheet_name, table_name, cell, value):
    applescript = f'''
    tell application "Numbers"
        tell sheet "{sheet_name}" of front document
            tell table "{table_name}"
                set value of cell "{cell}" to "{value}"
            end tell
        end tell
    end tell
    '''

    process = subprocess.Popen(['osascript', '-'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    stdout, stderr = process.communicate(applescript)

    if stderr:
        raise Exception(f"AppleScript Error: {stderr}")
