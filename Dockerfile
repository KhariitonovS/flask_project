FROM python

WORKDIR /flask_project

COPY . .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]