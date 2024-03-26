from mongoengine import *
import datetime
from os import getenv

db_params = getenv("DB_PARAMS")

connect(host=db_params)


class Captcha(Document):
    user_id = IntField()
    verified = BooleanField(default=False)
    data = IntField()
    created_at = DateTimeField()
    updated_at = DateTimeField(default=datetime.datetime.now())

class User(Document):
    user_id = IntField()
    from_user_id = IntField()
    solana_address = StringField()
    token_balance = FloatField()
    referral = StringField()
    ref_self= BooleanField(default=False)
    ref_used=BooleanField(default=False)
    verify_twitter_task = BooleanField(default=False)
    created_at = DateTimeField()
    updated_at = DateTimeField(default=datetime.datetime.now())