FROM python:3
ADD restapi_srv.py /
RUN pip install flask
RUN pip install pymongo
RUN pip install flask-restful
RUN pip install flask-jsonpify
CMD ["python","./restapi_srv.py"]
