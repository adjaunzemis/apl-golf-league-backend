# install python in the container
FROM python:3.12

# copy the local requirements.txt file to the 
# /app/requirements.txt in the container
# (the /app dir will be created)
COPY ./requirements.txt /app/requirements.txt

# install the packages from the requirements.txt file in the container
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# copy the local app folder to the app folder in the container
COPY ./app /app/

# copy configuration file into container
COPY .env .env

# execute command to start server
CMD ["python", "-m", "app.main"]
