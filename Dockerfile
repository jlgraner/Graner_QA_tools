FROM python:3

#Set OS var and tell Debian not to bug us with questions
ENV OS="Linux"
ARG DEBIAN_FRONTEND=noninteract

#Create destination for repository on the container
RUN mkdir -p /usr/src/app

#Copy the repository to a specific place in the container
#COPY mri_quickgifs.py /usr/src/app
#COPY neurodebian.gpg /usr/src/app
COPY . /usr/src/app

#Set up pip install requirements file
#COPY requirements.txt /usr/src/app

#Install python requirements using pip
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

##FROM FMRIPREP:
# Prepare environment
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    curl \
                    bzip2 \
                    ca-certificates \
                    xvfb \
                    cython3 \
                    build-essential \
                    autoconf \
                    libtool \
                    pkg-config \
                    git && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y --no-install-recommends \
                    nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Installing Neurodebian packages (FSL, AFNI, git)
RUN curl -sSL "http://neuro.debian.net/lists/$( lsb_release -c | cut -f2 ).us-ca.full" >> /etc/apt/sources.list.d/neurodebian.sources.list && \
    apt-key add /usr/src/app/neurodebian.gpg && \
    (apt-key adv --refresh-keys --keyserver hkp://ha.pool.sks-keyservers.net 0xA5D32F012649A5A9 || true)

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    #afni=16.2.07~dfsg.1-5~nd16.04+1 \
                    afni &&\
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#Add the AFNI path to PATH
ENV PATH="/usr/lib/afni/bin:$PATH"
##

#Set the container to pass things directly to mri_quickgifs.py
ENTRYPOINT ["python", "/usr/src/app/mri_quickgifs.py"]

CMD []