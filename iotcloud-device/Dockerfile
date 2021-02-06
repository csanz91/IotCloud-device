FROM python:3.9

# Cache lxml at the begining
RUN pip install lxml

# Create app directory
WORKDIR /app

# Install app dependencies
COPY ./requirements.txt ./
COPY ./libs ./libs
RUN pip install -r requirements.txt

# Bundle app source
COPY ./ /app

# Generate logs folder if it doesn't exist
RUN mkdir -p /app/logs

# Generate device data folder if it doesn't exist
RUN mkdir -p /app/device_data

# Generate config folder if it doesn't exist
RUN mkdir -p /app/config

WORKDIR /app/source
EXPOSE 5010
CMD ["gunicorn", "-b", "0.0.0.0:5010", "api:app"]