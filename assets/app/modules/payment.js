export default class Payment {
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
    this.stripeKey = $('#stripe_key');
    this.paymentErrors = $('.payment-errors');
    this.coupon = $('#coupon_code');
    this.couponCodeStatus = $('#coupon_code_status');
    this.name = $('#name');
    this.spinner = $('.spinner');
  }

  attachEvents() {
    let _this = this;

    let errors = {
      'missing_name': 'You must enter your name.'
    };

    if (this.stripeKey.length && this.stripeKey.val()) {
      Stripe.setPublishableKey(this.stripeKey.val());
    }

    $('body').on('submit', this.selector, function() {
      if (!_this.protectAgainstInvalidCoupon(_this.coupon, _this.couponCodeStatus)) {
        return false;
      }

      _this.spinner.show();
      _this.paymentErrors.hide();

      if (_this.name.val().length === 0) {
        _this.paymentErrors.text(errors.missing_name);
        _this.paymentErrors.show();
        _this.spinner.hide();
        _this.name.select();

        return false;
      }

      _this.container.find('button').prop('disabled', true);

      let stripeResponseHandler = function (status, response) {
        _this.paymentErrors.hide();

        if (response.error) {
          _this.spinner.hide();
          _this.container.find('button').prop('disabled', false);

          _this.paymentErrors.text(response.error.message);
          _this.paymentErrors.show();
        }
        else {
          // Token contains id, last 4 digits, and card type.
          let token = response.id;

          // Insert the token into the form so it gets submit to the server.
          let field = '<input type="hidden" id="stripe_token" name="stripe_token" />';
          _this.container.append($(field).val(token));

          // Process the payment.
          _this.spinner.show();
          _this.container.get(0).submit();
        }
      };

      Stripe.card.createToken(_this.container, stripeResponseHandler);

      return false;
    });
  }

  protectAgainstInvalidCoupon() {
    if (this.couponCodeStatus.is(":visible") && !this.couponCodeStatus.hasClass("alert-success")) {
      this.coupon.select();

      return false;
    }

    return true;
  }
};
