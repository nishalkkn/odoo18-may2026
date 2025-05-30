/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";


export class WebsiteTemplate extends Component {

    setup() {
        super.setup();
        this.orm = useService('orm');
        this.showPerformanceData();
        this.showMinificationData();
        this.showImageOptimizationData();
        this.showSeoData();
        this.checkInternalExternalSocialMediaLinks();
        this.checkRobotsTxt();
        this.seoFriendlyUrl();
        this.securityHeaders();
        this.cspComponents();

        this.searchOption();

        this.state = useState({
            performance_metrics : {},
            minification_metrics : {},
            img_optimization_metrics : {},

            seo_metrics : {},
            internal_external_social_metrics : {},
            robots_txt_metrics : {},
            url_seo_metrics : {},
            security_header_metrics : {},
            csp_metrics : {},

            search_option_metrics : {},
        });
    }

    //    showing performance data
    async showPerformanceData() {
        this.orm.call("website.performance.details", "performance_details", [], {}).then((result) => {
            this.state.performance_metrics = result
        });
    }
    //    show the minification data of html, css and js
    async showMinificationData() {
        this.orm.call("website.performance.details", "check_minification", [], {}).then((result) => {
            this.state.minification_metrics = result
        });
    }
    //    show the image optimization data
    async showImageOptimizationData() {
        this.orm.call("website.performance.details", "check_image_optimization", [], {}).then((result) => {
            this.state.img_optimization_metrics = result
        });
    }


    //    showing seo data
    async showSeoData() {
        this.orm.call("website.seo.details", "seo_details", [], {}).then((result) => {
            this.state.seo_metrics = result;
        });
    }

    async checkInternalExternalSocialMediaLinks(){
        this.orm.call("website.seo.details", "check_internal_external_social_media_links", [], {}).then((result) => {
            this.state.internal_external_social_metrics = result;
        });
    }

    async checkRobotsTxt(){
        this.orm.call("website.seo.details", "check_robots_txt", [], {}).then((result) => {
            this.state.robots_txt_metrics = result;
        });
    }

    async seoFriendlyUrl(){
        this.orm.call("website.seo.details", "is_url_seo_friendly", [], {}).then((result) => {
            this.state.url_seo_metrics = result;
        });
    }

    async securityHeaders() {
        this.orm.call("website.security.details", "check_security_headers", [], {}).then((result) => {
            this.state.security_header_metrics = result;
        });
    }
    async cspComponents() {
        this.orm.call("website.security.details", "check_csp_components", [], {}).then((result) => {
            this.state.csp_metrics = result;
        });
    }

    //    showing ui data
    async searchOption() {
        this.orm.call("website.ui.details", "check_search_option", [], {}).then((result) => {
            this.state.search_option_metrics = result;
        });
    }
}
WebsiteTemplate.template = "odoo_health_report_tool.WebsiteConfigurator"
registry.category("actions").add("website_health_configurator", WebsiteTemplate);
