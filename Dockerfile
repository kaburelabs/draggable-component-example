
FROM python:3.7-slim

# LABEL is optional (only provides some metadata about the image)
LABEL maintainer="MyOsh Staff name <enterprise_email>"
LABEL contractNo="XXXXXXXX"

# both files are explicitly required!
COPY Pipfile Pipfile.lock ./

RUN apt-get update && DEBIAN_FRONTEND="noninteractive" TZ="America/New_York" apt-get install -y tzdata && apt-get install -y apache2 && apt-get clean apt-get install apt-utils -y

RUN pip install pipenv && \
  apt-get update && \
  apt-get install -y --no-install-recommends gcc python3-dev libssl-dev && \
  pipenv install --deploy --system && \
  apt-get remove -y gcc python3-dev libssl-dev && \
  apt-get autoremove -y && \
  pip uninstall pipenv -y

# Sets the working directory inside of the container
WORKDIR /app

#Copy the files in the folder to /app folder inside of the image container 
COPY . /app

# CMD ["python", "app.py"]

EXPOSE 8000

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "app:server"]
