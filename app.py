from flask import Flask, redirect
from flask_graphql import GraphQLView
import graphene

from models import db_session
from schema import schema

app = Flask(__name__)

# Add a route for GraphQL, we will set this up with GraphiQL
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        context={'session': db_session},
        graphiql=True
    )
)

# Redirect the index to the GraphiQL interface
@app.route("/")
def index():
    return redirect("/graphql", code=302)

# Make sure to shut down the database session when the app is closed
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    app.run()