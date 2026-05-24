FROM python:3.8-slim

# Install PostgreSQL command-line tools
RUN apt-get update && apt-get install -y postgresql-client cron

COPY start.sh /app/start.sh 

# Copy the ELT script make sure to put .at the end The . at the end means "copy it to the current directory inside the container"
COPY elt_script.py . 

WORKDIR /app
#RUN EVERYDAY AT 3: 00 AM YOU CAN FIND ONLINE WHAT TO WRITE FOR WHAT TIME
RUN echo "0 3 * * * python /app/elt_script.py" | crontab - 

# Set the default command to run the ELT script
CMD ["python", "elt_script.py"]