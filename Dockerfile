FROM python:3.10
RUN apt update && apt install -y nano
RUN mkdir -p /root/app
COPY ./ /root/app
RUN pip install -r /root/app/requirements.txt
WORKDIR "/root/app/"
CMD [ "python3", "-u", "./main.py" ]
