import flatpickr from 'flatpickr';

export default class createCoupon {
  constructor(selector) {
    this.selector = selector;
    this.container = $(this.selector);

    this.isAttached = false;
    this.attach();
  }

  attach() {
    if (this.isAttached) return;
    if (this.container.length === 0) return;

    this.attachUI();
    this.attachEvents();
    this.isAttached = true;
  }

  attachUI() {
    this.durationSelector = '#duration';
    this.durationInMonths = $('#duration_in_months_wrapper');
    this.redeemBySelector = '#redeem_by';
    this.redeemByClearSelector = '.js-redeem-by-clear';
  }

  attachEvents() {
    let _this = this;

    $('body').on('change', this.durationSelector, function () {
      if ($(_this.durationSelector).val() === 'repeating') {
        _this.durationInMonths.show();
      }
      else {
        _this.durationInMonths.hide();
      }
    });

    let $flatpickr = $(this.redeemBySelector).flatpickr({
      enableTime: true,
      altInput: true,
      altFormat: 'F j, Y h:i K',
      dateFormat: 'Y-m-d H:i:ss',
      disable: [
        function(date) {
          return date < new Date().setHours(0, 0, 0, 0);
        }
      ]
    });

    $(this.redeemByClearSelector).click(function() {
       $flatpickr.clear();
    });
  }
};
