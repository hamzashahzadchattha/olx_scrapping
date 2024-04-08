from database.db import db
from models.models import Ad, OwnerInfo
import logging

def get_ads(request):
    limit = request.args.get('limit', None)
    order_by = request.args.get('order_by', None)
    filter_obj = {}

    for key in request.args:
        if key not in ['limit', 'order_by']:
            filter_obj[key] = request.args[key]

    ads = Ad.query \
        .filter_by(**filter_obj) \
        .order_by(order_by) \
        .limit(limit) \
        .all()

    return ads

def create_ad(db, body):
    try:
        owner_info_data = body.pop('owner_info', {})
        
        ad = Ad(**body)
        db.session.add(ad)
        db.session.commit()
        logging.info(f"Created ad: {ad}")

        if owner_info_data:
            logging.info(f"Creating owner_info with data: {owner_info_data}")
            owner_info = OwnerInfo(owner_info_data)
            owner_info.ad = ad
            db.session.add(owner_info)
            db.session.commit()
            logging.info(f"Created owner_info: {owner_info}")

        return ad
    except Exception as e:
        logging.error(f"Error creating ad: {e}")
        db.session.rollback()
        raise e


def get_ad_by_id(ad_id):
    ad = Ad.query \
            .join(OwnerInfo, isouter=True) \
            .filter(Ad.id == ad_id) \
            .first()

    return ad