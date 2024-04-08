from database.db import db
from datetime import datetime

class TimestampMixin:
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Ad(TimestampMixin, db.Model):
    __tablename__ = 'ad'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    ad_posted_at = db.Column(db.TIMESTAMP)
    ad_image = db.Column(db.String(255))
    kilometer_driven = db.Column(db.String(50))
    owner_info = db.relationship('OwnerInfo', back_populates='ad', uselist=False, cascade='all, delete')

    def __init__(self, title, price, location, ad_posted_at=None, ad_image=None, kilometer_driven=None):
        self.title = title
        self.price = price
        self.location = location
        self.ad_posted_at = ad_posted_at
        self.ad_image = ad_image
        self.kilometer_driven = kilometer_driven

    def serialize(self):
        owner_info = None
        if self.owner_info:
            owner_info = self.owner_info.serialize()

        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'location': self.location,
            'ad_posted_at': self.ad_posted_at,
            'ad_image': self.ad_image,
            'kilometer_driven': self.kilometer_driven,
            'created': self.created,
            'updated': self.updated,
            'owner_info': owner_info
        }


class OwnerInfo(db.Model):
    __tablename__ = 'owner_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    mobile = db.Column(db.String(20))
    whatsapp = db.Column(db.String(20))
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id', ondelete='CASCADE'))
    ad = db.relationship('Ad', back_populates='owner_info')

    def __init__(self, owner_info_data):
        self.name = owner_info_data.get('name')
        self.mobile = owner_info_data.get('mobile')
        self.whatsapp = owner_info_data.get('whatsapp')
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'mobile': self.mobile,
            'whatsapp': self.whatsapp
        }

