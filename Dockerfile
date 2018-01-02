FROM python:2.7
ADD restapi_srv.py /
RUN pip install flask
RUN pip install mongoqueue
RUN pip install pymongo==2.7.2
RUN pip install flask-restful
RUN pip install flask-jsonpify
CMD ["python","./restapi_srv.py"]
