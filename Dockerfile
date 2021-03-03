FROM nginx/unit:1.22.0-python3.9

# install and cleanup (saving python3-six)
COPY requirements.txt /config/requirements.txt
RUN pip install --no-cache-dir -r /config/requirements.txt

COPY app /www/app

EXPOSE 80
