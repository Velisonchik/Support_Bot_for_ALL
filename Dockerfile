FROM python:slim
LABEL dest="for ALL"
WORKDIR /bot_for_all
COPY . /bot_for_all
RUN pip install -r /bot_for_all/requirements.txt
CMD ["python3", "/bot_for_all/main_bot.py"]
