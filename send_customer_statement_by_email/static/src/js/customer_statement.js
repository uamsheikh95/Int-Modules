odoo.define('account_customer_statement.report_partnerledger_custom', function (require) {
"use strict";
  function send_email() {
    var Model = require('web.Model');
    $(".send_email").click(function() {
      console.log('------------------------------')
    }
  }
});

// odoo.define('send_customer_statement_by_email.customer_statement', function (require) {
// "use strict";
// var form_widget = require('web.form_widgets');
// var core = require('web.core');
// var _t = core._t;
// var QWeb = core.qweb;
// var Model = require('web.Model')
// var custom_model = new Model('account.common.partner.report')
// form_widget.WidgetButton.include({
//     on_click: function() {
//          if(this.node.attrs.custom === "click"){
//             custom_model.call('action_statement_send')
//          return;
//          }
//          this._super();
//     },
// });
// });
