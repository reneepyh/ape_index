FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV TZ=Asia/Taipei
RUN ln -sf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

COPY run_pipeline.sh /app/run_pipeline.sh

RUN chmod +x /app/run_pipeline.sh

RUN mkdir -p /var/log && touch /var/log/pipeline.log

CMD ["/app/run_pipeline.sh"]
