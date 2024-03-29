FROM python

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY .env .
CMD [ "python3", "./bot.py" ]