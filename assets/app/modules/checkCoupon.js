import debounce from 'modules/debounce';

export default class CheckCoupon {
  constructor(selector, csrfToken) {
    this.selector = selector;
    this.container = $(this.selector);
    this.csrfToken = csrfToken;

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
    this.couponCodeStatus = $('#coupon_code_status');
    this.paymentAmount = $('.js-payment-amount');
  }

  attachEvents() {
    let _this = this;

    $('body').on('keyup', this.selector, debounce(function () {
      if (_this.container.val().length === 0) {
        _this.updatePaymentAmount();
        _this.couponCodeStatus.hide();

        return false;
      }

      _this.check();
    }, 300));

    $('body').on('submit', this.selector, function () {
      _this.spinner.show();
      _this.container.find('button').prop('disabled', true);
      _this.check();

      return false;
    });

    $('body').on('submit', this.coinBundlesSelector, function () {
      _this.check();

      return false;
    });

    if (this.container.val()) {
      this.container.trigger('keyup');
    }
  }

  check() {
    let _this = this;

    let ajaxParams = {
      type: 'POST',
      url: '/subscription/coupon_code',
      data: {
        coupon_code: this.container.val().toUpperCase()
      },
      dataType: 'json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader('X-CSRFToken', _this.csrfToken);
        return _this.couponCodeStatus.text('')
          .removeClass('alert-success alert-warning alert-danger').hide();
      }
    };

    return $.ajax(ajaxParams).done(function (data, status, xhr) {
      }).done(function (data, status, xhr) {
        let code = xhr.responseJSON.data;
        let newPaymentAmount = xhr.responseJSON.payment_amount;
        let amount = `${_this.discountType(code.percent_off, code.amount_off)} off`;
        let duration = _this.discountDuration(code.duration, code.duration_in_months);

        _this.updatePaymentAmount(code.percent_off, code.amount_off);

        return _this.couponCodeStatus.addClass('alert-success').text(amount + duration);
      }).fail(function (xhr, status, error) {
        let statusClass = 'alert-danger';

        if (xhr.status === 404) statusClass = 'alert-warning';

        _this.updatePaymentAmount();

        return _this.couponCodeStatus.addClass(statusClass).text(xhr.responseJSON.error);
      }).always(function (xhr, status, error) {
        _this.couponCodeStatus.show();

        return _this.container.val();
      });
  }

  discountType(percentOff, amountOff) {
    if (percentOff) return `${percentOff}%`;

    return `$${amountOff}`;
  }

  discountDuration(duration, durationInMonths) {
    switch (duration) {
      case 'forever':
      {
        return ' forever';
      }
      case 'once':
      {
        return ' first payment';
      }
      default:
      {
        return ` for ${durationInMonths} months`;
      }
    }
  }

  updatePaymentAmount(percentOff, amountOff) {
    let percentOffDefault = 0;
    let amountOffDefault = 0;

    if (percentOff) percentOffDefault = percentOff * 0.01;
    if (amountOff) amountOffDefault = amountOff;

    this.paymentAmount.each(function(index) {
      let newAmount = ($(this).data('amount') * (1 - percentOffDefault)) * 0.01;

      newAmount -= amountOffDefault;
      if (newAmount < 0) newAmount = 0;
      newAmount = newAmount.toFixed(2);

      $(this).text(newAmount);
    });
  }
};
