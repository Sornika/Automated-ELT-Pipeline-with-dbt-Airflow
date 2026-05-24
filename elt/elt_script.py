import subprocess
import time


def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available."""
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True)
            if "accepting connections" in result.stdout: #if postgresql replies accepting coonection i.e database is ready
                print("Successfully connected to PostgreSQL!")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay_seconds) #wait for delay_second second
    print("Max retries reached")
    return False


# Use the function before running the ELT process
if not wait_for_postgres(host="source_postgres"): #calling the function and if not ready stop all and (this function will be true if the connection fails
    exit(1)

print("Starting ELT script...")

# Configuration for the source PostgreSQL database
# the login details for the source database
source_config = {
    'dbname': 'source_db',
    'user': 'postgres',
    'password': 'secret',
    # Use the service name from docker-compose as the hostname
    'host': 'source_postgres'
}

# Configuration for the destination PostgreSQL database
#Just the login details for the destination database
destination_config = {
    'dbname': 'destination_db',
    'user': 'postgres',
    'password': 'secret',
    # Use the service name from docker-compose as the hostname
    'host': 'destination_postgres'
}

# Use pg_dump to dump the source database to a SQL file
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w'  # Do not prompt for password
]

# Set the PGPASSWORD environment variable to avoid password prompt
subprocess_env = dict(PGPASSWORD=source_config['password'])

# Execute the dump command
subprocess.run(dump_command, env=subprocess_env, check=True)

# Use psql to load the dumped SQL file into the destination database
load_command = [
    'psql', #psql = the tool that imports data into the database
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a', '-f', 'data_dump.sql'
]

# Set the PGPASSWORD environment variable for the destination database
subprocess_env = dict(PGPASSWORD=destination_config['password'])

# Execute the load command
subprocess.run(load_command, env=subprocess_env, check=True)

print("Ending ELT script...")