FROM nginx/unit:1.21.0-python3.7

# install and cleanup (saving python3-six)
COPY requirements.txt /config/requirements.txt
RUN apt update && apt install -y python3-pip                                  \
    && pip3 install -r /config/requirements.txt                               \
    && apt remove -y python3-pip                                              \
    && apt autoremove --purge -y                                              \
    && apt install -y python3-six                                             \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list

COPY app /www/app

EXPOSE 80
