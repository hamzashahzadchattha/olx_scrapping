# Olx Scrapper


## Libraries and tools used

- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [FlaskSQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [CORS](https://flask-cors.readthedocs.io/en/latest/)
- [PostgreSQL](https://www.postgresql.org/)
- [Fetch](https://developer.mozilla.org/pt-BR/docs/Web/API/Fetch_API/Using_Fetch)
- [PEP8](https://www.python.org/dev/peps/pep-0008/)

## Dependencies

- [Python3.x](https://www.python.org/)
- [PostgreSQL](https://www.postgresql.org/)

## How to run

### Install and configure PostgreSQL

The tutorial below refers to Unix-based systems.

First, you have to download and configure the PostgreSQL database. After that, create a superuser:

```
sudo -u postgres createuser --superuser username
```

After, create a database using the created user account:

```
sudo -u username createdb database_name
```

Now, you can access the created database:

```
psql -U username -d database_name
```

**All tutorials below, you must enter the backend folder.**

### Install python dependencies


You can install the dependencies in two ways:

1. Using Virtual Rnvironment :

    ```
    python3 -m venv env
    ```

2. Using pip3:

    ```
    pip install -r requirements.txt
    ```

### Configure environment variables

You need to create an .env file following the .env.example file.

```
APP_SETTINGS=
DATABASE_URL=
BEARER_TOKEN=
REFRESH_TOKEN=
REFRESH_TOKEN_ENDPOINT=
```

The APP_SETTINGS variable can be:

- config.config.DevelopmentConfig for development
- config.config.ProductionConfig for production
- config.config.StagingConfig for staging
- config.config.TestingConfig for testing

The DATABASE_URL variable is your database url. If you are using in localhost, the URL is something like: `postgresql:///database_name`.

### Run migrations

1.  ```
    python manage.py db init
    ```

2.  ```
    python manage.py db migrate
    ```

3.  ```
    python manage.py db upgrade
    ```

### Run the server

```
python manage.py runserver
```

The server will be running on `http://127.0.0.1:5000/`

### Frontend

You can just open the index.html file in the browser or you can run:

```
python -m http.server 5500
```

## API Endpoints

- [POST scrape/](docs/scrape_car_ads.md)
- [GET  ads/](docs/get_scraped_ads.md)
- [GET ads/:id](docs/get_ad_details.md)