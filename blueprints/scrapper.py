from database.db import db
from flask import Blueprint, request
from utils.decorators import validate_json
from utils.http import ok,not_found
from database.helper import get_ads, get_ad_by_id
from utils.scrapper_utils import OlxScraper

ads_blueprint = Blueprint('ads_blueprint', __name__)


@ads_blueprint.route('/ads/', methods=['GET', 'POST'])
@validate_json(ignore_methods=['GET'])
def ads():
    if request.method == 'GET':
        ads = get_ads(request)
        print("new", ads)
        return ok(ads)


@ads_blueprint.route('/ads/<int:id>/', methods=['GET'])
@validate_json(ignore_methods=['GET'])
def ad(id):
    ad_exists = get_ad_by_id(id)
    if ad_exists is None:
        return not_found('ad')

    if request.method == 'GET':
        return ok(ad_exists)


@ads_blueprint.route('/scrape/', methods=['POST'])
def scrape_olx():
    data_input = request.get_json()
    website_url = "https://www.olx.com.pk/islamabad-capital-territory_g2003003/q-cars"
    if "page_number" in data_input and data_input["page_number"] != None:
        page_number = data_input["page_number"]
        website_url = f"{website_url}/page={page_number}"

    data = {
        "website": website_url
    }

    olx_scraper = OlxScraper(data)
    olx_scraper.scrape_olx()

    return {'message': 'Scraping initiated successfully'}, 200