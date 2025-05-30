from odoo import models, api
from odoo.http import request
from requests import get
from bs4 import BeautifulSoup
from lxml import html
import requests
from urllib.parse import urljoin


class WebsitePerformanceDetails(models.Model):
    _name = 'website.performance.details'
    _description = "Website Performance Details"

    rootUrl = request.httprequest.url_root

    @api.model
    def performance_details(self):
        """function for finding the performance details of the odoo website"""
        try:
            response = get(self.rootUrl)
            status_code = response.status_code
            page_size = round(len(response.content) / 1024, 2)  # size in kb
            return {
                'status_code': status_code,
                'page_size': page_size,
                "status": "Up" if status_code == 200 else "Down",
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'Error',
                'message': 'Failed to access the website.',
                'error': str(e),
            }
        except Exception as e:
            return {
                'status': 'Error',
                'message': 'An unexpected error occurred.',
                'error': str(e),
            }

    @api.model
    def check_minification(self):
        """combine the result of minification of js, css and js"""
        response = get(self.rootUrl)
        tree = html.fromstring(response.content)
        # finding the css and js files
        css_files = tree.xpath('//link[@rel="stylesheet"]/@href')
        js_files = tree.xpath('//script[@src]/@src')

        return {
            "is_css_minified": self.check_files_minified(css_files),
            "is_js_minified": self.check_files_minified(js_files),
            "is_html_minified": self.check_html_minified(response.text),
            "css_files": css_files,
            "js_files": js_files,
        }

    def check_files_minified(self, files):
        """Checking the js and css files are minified or not"""
        minified = []
        for file in files:
            if file.endswith('.min.css') or file.endswith('.min.js'):
                minified.append(True)
            else:
                minified.append(False)
        return all(minified)

    def check_html_minified(self, html_content):
        """ Check if HTML has newlines or excessive spaces, which is a simple minification check"""
        original_size = len(html_content)
        minified_size = len(html_content.replace(" ", "").replace("\n", ""))
        return original_size == minified_size

    @api.model
    def check_image_optimization(self):
        """check the images in the website is optimised or not"""
        response = get(self.rootUrl)
        images = list(set(BeautifulSoup(response.content, "html.parser").find_all('img')))
        optimized = []
        not_optimized = []
        for img in images:
            src = img.get('src')
            if not src:
                continue  # Skip images without a source
            # Handle relative URLs if necessary
            image_url = urljoin(response.url, src)
            try:
                # Fetch the image
                img_response = requests.get(image_url, stream=True)
                img_response.raise_for_status()
                # Check file size (example threshold: 500KB)
                file_size_kb = int(img_response.headers.get('content-length', 0)) / 1024
                if file_size_kb > 500:
                    not_optimized.append(image_url)
                    continue
                # Check file extension
                valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                if not any(image_url.lower().endswith(ext) for ext in valid_extensions):
                    not_optimized.append(image_url)
                    continue
                # If all checks pass, the image is optimized
                optimized.append(image_url)
            except Exception:
                not_optimized.append(image_url)
        return {
            "images": len(images),
            "optimised_images_count": len(optimized),
            "optimised_images": optimized,
            "not_optimised_images": not_optimized,
            "not_optimised_images_count": len(not_optimized),
        }
