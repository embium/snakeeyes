import 'modules/bootstrap';

import FormatTimes from 'modules/formatTimes';
import BulkDelete from 'modules/bulkDelete';
import CreateCoupon from 'modules/createCoupon';
import CheckCoupon from 'modules/checkCoupon';
import Payment from 'modules/payment';
import Bet from 'modules/bet';

$(document).ready(function() {
  let csrfToken = $('meta[name=csrf-token]').attr('content');

  // TODO: If you want to enable Bootstrap JS components such as tooltips then
  // place those snippets of code here. Also don't forget to uncomment them
  // in both the modules/bootstrap.js file and in the SCSS at app.scss.
  // For example, to enable tooltips:
  //   $('[data-toggle="tooltip"]').tooltip();

  new FormatTimes('.js-from-now', '.js-short-date');
  new BulkDelete('#bulk_actions');
  new CreateCoupon('#duration_in_months_wrapper');
  new CheckCoupon('#coupon_code', csrfToken);
  new Payment('#subscription_form');
  new Payment('#payment_form');
  new Bet('#place_bet', csrfToken);
});
