def clean_file(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Remove null bytes
    clean_content = content.replace(b'\x00', b'')
    
    # Write back
    with open(filepath, 'wb') as f:
        f.write(clean_content)

if __name__ == '__main__':
    clean_file('data_wiping_tool/gui.py')
