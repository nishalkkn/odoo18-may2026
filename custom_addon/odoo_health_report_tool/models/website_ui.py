from odoo import models, api
from requests import get
from bs4 import BeautifulSoup
from odoo.http import request


class WebsiteUiDetails(models.Model):
    _name = 'website.ui.details'
    _description = "Website Ui Details"

    rootUrl = request.httprequest.url_root
    # rootUrl = "http://localhost:8018/contactus/"

    # @api.model
    # def ui_details(self):
    #     """function for finding the ui details of the odoo website"""
    #     try:
    #         response = get(self.rootUrl)
    #         search_option = self.check_search_option(response)
    #         return {
    #             "search_option": search_option,
    #         }
    #     except requests.exceptions.RequestException as e:
    #         return {
    #             'status': 'Error',
    #             'message': 'Failed to access the website.',
    #             'error': str(e),
    #         }
    #     except Exception as e:
    #         return {
    #             'status': 'Error',
    #             'message': 'An unexpected error occurred.',
    #             'error': str(e),
    #         }

    @api.model
    def check_search_option(self):
        """check the search option in the website"""
        response = get(self.rootUrl)
        soup = BeautifulSoup(response.text, 'html.parser')
        search_input = soup.find('input', {'type': 'text'}) or soup.find('input', {'type': 'search'})
        return {
            "search_option": search_input,
        }
