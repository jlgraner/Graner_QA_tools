FROM python:3

#Create destination for repository on the container
RUN mkdir -p /usr/src/app

#Copy the repository to a specific place in the container
COPY . /usr/src/app

#Install python requirements using pip
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

#Set the container to pass things directly to mri_quickgifs.py
ENTRYPOINT ["python", "/usr/src/app/mri_quickgifs.py"]

CMD []