FROM python:3-buster
COPY ./papi/ /papi/
RUN mkdir keys
RUN ssh-keygen -q -t rsa -N '' -f /keys/id_rsa
RUN ssh-keygen -t ecdsa -b 256 -m PEM -f jwtRS256.key -N ''
RUN cat jwtRS256.key
RUN mv jwtRS256.key keys/private.pem
RUN mv jwtRS256.key.pub keys/public.pem
#COPY ./keys/ /keys/
COPY ./main.py /
COPY ./config.py /
COPY ./setup.py /
RUN python setup.py install
EXPOSE 5000
CMD [ "python", "./main.py" ]
