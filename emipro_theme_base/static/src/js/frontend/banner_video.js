odoo.define('emipro_theme_base.banner_video', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    publicWidget.registry.js_banner_video = publicWidget.Widget.extend({
        selector: ".js_banner_video",
        start: function () {
            this.redrow();
        },
        stop: function () {
            this.clean();
        },
        redrow: function (debug) {
            this.clean(debug);
            this.build(debug);
        },
        clean: function (debug) {
            this.$target.empty();
        },
        build: function (debug) {
            var self = this;
                ajax.jsonRpc('/get_banner_video_data', 'call').then(function (data) {
                    $(self.$target).html(data);
                });
        }
    });
})