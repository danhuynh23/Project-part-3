import subprocess
import os

def run_mysql_dump():
    # Path where you want to save the dump on the host machine
    dump_file = 'dumpfile.sql'
    
    # Command to run mysqldump inside the mysql container
    command = [
        'docker', 'exec', '-i', 'mysql-container',
        'mysqldump', '-u', 'root', '-pmy-secret-pw', 'airticketingsystem'
    ]
    
    with open(dump_file, 'wb') as f:
        # Execute the command and write the output to the dump file
        subprocess.run(command, stdout=f)
        print(f"Database dump saved to {dump_file}")

# Run the dump
run_mysql_dump()
