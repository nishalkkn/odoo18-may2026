from odoo import models, api
from odoo.http import request
import requests
from requests import get
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from urllib.parse import urlparse


class WebsiteSeoDetails(models.Model):
    _name = 'website.seo.details'
    _description = "Website Seo Details"

    rootUrl = request.httprequest.url_root

    @api.model
    def seo_details(self):
        """function for finding the performance details of the odoo website"""
        try:
            response = get(self.rootUrl)
            soup = BeautifulSoup(response.content, "html.parser")
            return {
                "title": soup.title.string if soup.title else "No Title",
                "meta_description": soup.find("meta", attrs={"name": "description"})["content"]
                if soup.find("meta", attrs={"name": "description"}) else "No Meta Description",
                "keywords": soup.find("meta", attrs={"name": "keywords"})["content"]
                if soup.find("meta", attrs={"name": "keywords"}) else "No Keywords",
                "tag_counts": {
                    "h1 tag": len(soup.find_all("h1")),
                    "h2 tag": len(soup.find_all("h2")),
                    "h3 tag": len(soup.find_all("h3")),
                    "img tag": len(soup.find_all("img")),
                    "a tag": len(soup.find_all("a")),
                    "p tag": len(soup.find_all("p")),
                },
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
    def check_internal_external_social_media_links(self):
        """check internal , external and social media links"""
        response = get(self.rootUrl)
        soup = BeautifulSoup(response.content, "html.parser")
        base_url = urlparse(self.rootUrl).netloc
        social_media_domains = {
            "Facebook": "facebook",
            "X": "twitter",
            "Instagram": "instagram",
            "Linkedin": "linkedin",
            "Youtube": "youtube",
            "Pinterest": "pinterest",
            "Whatsapp": "wa.me",
            "Github": "github",
            "TikTok": "tiktok"
        }
        internal_links = []
        external_links = []
        social_media_links = {}
        for val in soup.find_all('a', href=True):
            full_url = urljoin(self.rootUrl, val['href'])
            parsed_url = urlparse(full_url)
            # internal links & external links
            if parsed_url.netloc == base_url:
                internal_links.append(full_url)
            else:
                external_links.append(full_url)
            # social media links
            for platform, domain in social_media_domains.items():
                if domain in full_url.lower():
                    if platform not in social_media_links:
                        social_media_links[platform] = []
                    if full_url not in social_media_links[platform]:
                        social_media_links[platform].append(full_url)
        internal_links = list(set(internal_links))
        external_links = list(set(external_links))
        return {
            "internal_links_count": len(internal_links),
            "internal_links": internal_links,
            "external_links_count": len(external_links),
            "external_links": external_links,
            "social_media_links": social_media_links,
        }

    @api.model
    def check_robots_txt(self):
        """checking the presence of robots.txt in the website"""
        url = self.rootUrl
        # Ensure the URL ends with /
        if not url.endswith('/'):
            url += '/'
        # Append robots.txt to the URL
        robots_url = url + "robots.txt"
        robots_response = requests.get(robots_url, timeout=10)
        # Append sitemap.xml to the URL
        sitemap_url = url + "sitemap.xml"
        sitemap_response = requests.get(robots_url, timeout=10)
        return {
            "robots_txt": robots_url,
            "robots_txt_status_code": robots_response.status_code,
            "sitemap_xml": sitemap_url,
            "sitemap_xml_status_code": sitemap_response.status_code,
        }

    def check_redirects(self, url):
        """checking the redirects in the web page"""
        # Send a GET request with redirects enabled
        response = requests.get(url, allow_redirects=True, timeout=10)
        # Print final URL after all redirects
        print(f"Final URL after redirects: {response.url}")
        # List of all redirects (if any)
        print(response.history)
        if response.history:
            print("Redirect chain:")
            for resp in response.history:
                print(f"{resp.status_code} -> {resp.url}")
        else:
            print("No redirects. Direct URL access.")
        # Status Code of the final URL
        print(f"Final response status code: {response.status_code}")

    @api.model
    def is_url_seo_friendly(self):
        """Check if the website URL is SEO-friendly or not.
        Returns a tuple of (is_friendly: bool, issues: list)"""
        url = self.rootUrl
        try:
            parsed_url = urlparse(url)
            url_seo_issues = []
            # stop words
            stop_words = {
                'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
                'the', 'to', 'was', 'were', 'will', 'with'
            }
            # Check for HTTPS
            if parsed_url.scheme != "https":
                url_seo_issues.append("URL is not using HTTPS")
            # Check domain case
            if any(char.isupper() for char in parsed_url.netloc):
                url_seo_issues.append("Domain contains uppercase letters")
            # Get path without leading/trailing slashes
            path = parsed_url.path.strip('/')
            if path:
                # Check for special characters (allowing hyphens)
                if re.search(r'[^a-z0-9\-/]', path.lower()):
                    url_seo_issues.append("URL contains special characters")
                # Check for consecutive hyphens
                if '--' in path:
                    url_seo_issues.append("URL contains consecutive hyphens")
                # Check for uppercase letters
                if any(char.isupper() for char in path):
                    url_seo_issues.append("URL contains uppercase letters")
                # Check for underscores
                if '_' in path:
                    url_seo_issues.append("URL contains underscores instead of hyphens")
                # Check path segments for stop words and length
                path_segments = path.split('/')
                for segment in path_segments:
                    words = segment.split('-')
                    stop_words_found = [word for word in words if word.lower() in stop_words]
                    if stop_words_found:
                        url_seo_issues.append(f"URL contains stop words: {', '.join(stop_words_found)}")
                    # Check segment length
                    if len(segment) > 100:
                        url_seo_issues.append("URL path segment is too long")
            # Check for length (should not exceed 2083 characters)
            if len(url) > 2083:
                url_seo_issues.append("URL is too long (exceeds 2083 characters)")
            # Check for query parameters
            if parsed_url.query:
                url_seo_issues.append("URL contains query parameters")
            # Check for URL fragments
            if parsed_url.fragment:
                url_seo_issues.append("URL contains fragments (#)")
            return {
                "is_seo_friendly_url": not bool(url_seo_issues),
                "seo_url_issues": url_seo_issues,
            }
        except Exception as e:
            return False, [f"Invalid URL format: {str(e)}"]
