from odoo import models, api
from requests import get
from odoo.http import request


class WebsiteSecurityDetails(models.Model):
    _name = 'website.security.details'
    _description = "Website Security Details"

    rootUrl = request.httprequest.url_root
    # rootUrl = "http://localhost:8018/contactus"

    # @api.model
    # def security_details(self):
    #     """function for finding the security details of the odoo website"""
    #     try:
    #         response = get(self.rootUrl)
    #         return {
    #             # "csp": csp_components,
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
    def check_security_headers(self):
        """checking security headers"""
        response = get(self.rootUrl)
        header_components = ["Strict-Transport-Security",
                             "X-Content-Type-Options",
                             "X-Frame-Options",
                             "Referrer-Policy",
                             "Permissions-Policy",
                             "Cross-Origin-Resource-Policy",
                             "Cache-Control",
                             "Expect-CT",
                             "Access-Control-Allow-Origin",
                             "X-XSS-Protection",
                             "Content-Encoding"]
        security_headers = {}
        for component in header_components:
            security_headers[component] = response.headers.get(component, 'Not Set')
        return {
            "security_headers": security_headers,
        }

    @api.model
    def check_csp_components(self):
        """checking csp components"""
        response = get(self.rootUrl)
        csp = response.headers.get('Content-Security-Policy')
        csp_components = [
            "default-src", "script-src", "style-src", "img-src", "connect-src",
            "font-src", "object-src", "media-src", "frame-src", "child-src",
            "manifest-src", "worker-src", "form-action", "frame-ancestors",
            "block-all-mixed-content", "upgrade-insecure-requests", "require-trusted-types-for", "trusted-types"
        ]
        detected_components = {component: "Not Present" for component in csp_components} if not csp else {
            component: "Present" if component in csp else "Not Present" for component in csp_components}
        return {
            "csp": detected_components,
        }
