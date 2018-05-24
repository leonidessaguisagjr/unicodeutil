FROM pypy:3

# Set the working directory
WORKDIR /ucdwebapp

# Copy the files
COPY requirements.txt /ucdwebapp/

COPY app.py /ucdwebapp/

COPY static/* /ucdwebapp/static/

COPY templates/* /ucdwebapp/templates/

# Run pip to install the required packages
RUN pip install --no-cache-dir --trusted-host=pypi.python.org -r requirements.txt

# Unblock port 8080
EXPOSE 8080

# Start the web app
ENTRYPOINT ["gunicorn", "--bind=:8080", "app:app"]
