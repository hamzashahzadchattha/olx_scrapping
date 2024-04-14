from utils.errors import BadRequestException

## will use for put and post requests in future

def validate_create_body(body: dict) -> None:
    _validate_presence_of_fields(body, ['title', 'price', 'location', 'ad_posted_at', 'ad_url', 'kilometer_driven'])
    _validate_data_types(body)

def validate_update_body(body: dict) -> None:
    _validate_data_types(body)

def _validate_presence_of_fields(body: dict, required_fields: list) -> None:
    for field in required_fields:
        if field not in body:
            raise BadRequestException(f'Missing {field} parameter.')

def _validate_data_types(body: dict) -> None:
    validations = {
        'title': str,
        'price': int,
        'location': str,
        'ad_posted_at': str,
        'ad_url': str,
        'kilometer_driven': str
    }

    for field, data_type in validations.items():
        if field in body and not isinstance(body[field], data_type):
            raise BadRequestException(f'Invalid data type for {field}. Expected {data_type.__name__}.')
