From python:3.11-slim

# prevent python from writting .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# ensure logs are printed directly to the logs
ENV PYTHONBUFFERED 1 

WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/list/*

# install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# copy the rest of the code into the container
COPY . /app/

EXPOSE 8000

# define the command to start the app using Gunicorn

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "muturaa_net.wsgi:application"]
