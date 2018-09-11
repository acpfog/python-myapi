# Build an intermediate image with packages and requirements
FROM python:3.6-alpine as build
MAINTAINER Volodymyr Larkin <vlarkin@gmail.com>
RUN apk add --update --no-cache gcc musl-dev postgresql-dev python3-dev
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Build a final small image 
FROM python:3.6-alpine
COPY --from=build /usr/local/lib/python3.6/site-packages/ /usr/local/lib/python3.6/site-packages/
RUN apk add --update --no-cache postgresql-client      && \
    find / -type d -name __pycache__ -exec rm -r {} +  && \
    rm -r /usr/local/lib/python*/ensurepip             && \
    rm -r /usr/local/lib/python*/lib2to3               && \
    rm -r /usr/local/lib/python*/turtledemo            && \
    rm -r /usr/local/lib/python*/idlelib               && \
    rm /usr/local/lib/python*/turtle.py                && \
    rm /usr/local/lib/python*/webbrowser.py            && \
    rm /usr/local/lib/python*/doctest.py               && \
    rm /usr/local/lib/python*/pydoc.py                 && \
    rm -rf /root/.cache /var/cache /usr/share/terminfo && \
    mkdir /app
COPY myapi.py /app
WORKDIR /app
EXPOSE 5000
CMD ["python", "myapi.py"]
