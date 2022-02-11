# install python in the container
FROM python:3.8

# copy the local requirements.txt file to the 
# /app/requirements.txt in the container
# (the /app dir will be created)
COPY ./requirements.txt /app/requirements.txt

# install the packages from the requirements.txt file in the container
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# copy the local app folder to the app fodler in the container
COPY ./app /app

# TODO: set environment variables in VM

# execute command to start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
