# Shopify Summer 2019 Intern Challenge

This is a solution to the Shopify Summer 2019 intern challenge.

### Installing

The project was built with Python 3.7.2. Make sure you have Python 3.7.2 and pip installed.

##### Installing dependencies

```
pip install flask
pip install flask_graphql
pip install sqlalchemy
pip install graphene
pip install graphene_sqlalchemy
pip install graphql_relay
```

_**Note:** You may have to use pip3 instead of pip_

##### Running

To run the app you can either use `python app.py` (or `python3 app.py`) or by setting the `FLASK_APP` environment variable to `FLASK_APP=app.py` and running with `flask run`.

The app should now be live at http://localhost:5000/

### Project Breakdown
* `app.py` contains the main app and routes
* `schema.py` contains the GraphQL schema
* `models.py` contains the database models
* `database.db` prepopulated database as an example

### API

The app is built with GraphQL and exposes the endpoint with [GraphiQL](https://github.com/graphql/graphiql) so all you need to do to start running queries and mutations is navigate to http://localhost:5000/graphql. API documentation can also be found through the GraphiQL interface on the right.

