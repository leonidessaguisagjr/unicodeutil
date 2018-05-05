FROM python:3.6.5

# Set the working directory
WORKDIR /ucdwebapp

# Copy the files
COPY requirements.txt /ucdwebapp/

COPY app.py /ucdwebapp/

COPY static/* /ucdwebapp/static/

COPY templates/* /ucdwebapp/templates/

# Run pip to install the required packages
RUN pip install --trusted-host=pypi.python.org -r requirements.txt

# Unblock the default port for Flask
EXPOSE 5000

# Start the Flask app
CMD ["python3", "app.py"]
