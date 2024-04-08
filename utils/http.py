from database.db import db
from typing import List, Union
from models.models import Ad
from flask import Response, jsonify
from werkzeug.wrappers import Response as ResponseType
from typing import Iterable

def ok(resource: Union[db.Model, Iterable[db.Model]]) -> ResponseType:
    """
    Helper function that returns an HTTP status code 200 and the
    serialized model(s) using the `serialize` method.

    Args:
        resource (Union[db.Model, Iterable[db.Model]]): A single model instance or an iterable of model instances.

    Returns:
        ResponseType: A Flask response object with the serialized data.
    """
    if isinstance(resource, db.Model):
        return jsonify(resource.serialize())

    return jsonify([res.serialize() for res in resource])


def no_content() -> ResponseType:
    """
    Helper function that returns an http status code 204.
    """

    return Response(status=204)


def created(model: db.Model) -> ResponseType:
    """
    Helper function that returns an http status code 201 and the
    serialized model.

    @param model: Model to be serialized
    """

    return jsonify(model.serialize()), 201


def bad_request(exception: Exception) -> ResponseType:
    """
    Helper function that returns an http status code 400 and an error message.

    @param exception: The exception throwed.
    """

    return Response(response=str(exception), status=400)


def not_found(resource: str) -> ResponseType:
    """
    Helper function that returns an http status code 404.

    @param resource: Resource name that was not found.
    """

    return Response(response=f'{resource} not found.'.capitalize(), status=404)


def not_allowed() -> ResponseType:
    """
    Helper function that returns an http status code 405.
    """

    return Response(response='Method not allowed.', status=405)


def internal_error() -> ResponseType:
    """
    Helper function that returns an http status code 500.
    """

    return Response(response='Internal Error.', status=500)
