export default class Bet {
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
    this.guess = $('#guess');
    this.wagered = $('#wagered');
    this.dice = $('#dice');
    this.userCoins = $('#user_coins');
    this.outcomeStatus = $('#outcome');
    this.spinner = $('.spinner');
    this.recentBetsSelector = '#recent_bets';
  }

  attachEvents() {
    let _this = this;

    $('body').on('submit', this.selector, function () {
      _this.spinner.show();
      _this.container.find('button').prop('disabled', true);
      _this.create();

      return false;
    });
  }

  create() {
    let _this = this;

    let ajaxParams = {
      type: 'POST',
      url: '/bet/place',
      data: {
        guess: $(this.guess).val(),
        wagered: $(this.wagered).val()
      },
      dataType: 'json',
      beforeSend: function (xhr) {
        xhr.setRequestHeader('X-CSRFToken', _this.csrfToken);
        return _this.outcomeStatus.text('')
          .removeClass('alert-success alert-warning alert-danger alert-info').hide();
      }
    };

    return $.ajax(ajaxParams).done(function (data, status, xhr) {
      let coinsLeft = parseInt(_this.userCoins.text());
      let parsedData = xhr.responseJSON.data;
      let statusHTML = '';
      let betClass = '';
      let alertClass = '';
      let diceEntities = '';

      _this.userCoins.text(coinsLeft + parsedData.net);

      if (parsedData.is_winner) {
        statusHTML = '<i class="far fa-fw fa-smile"></i> Congrats, you won!';
        betClass = 'success';
        alertClass = 'success';
      } else {
        statusHTML = '<i class="far fa-fw fa-frown"></i> You lost, try again!';
        betClass = 'danger';
        alertClass = 'info';
      }

      diceEntities += `&#x268${(parseInt(parsedData.die_1) - 1)}; `;
      diceEntities += `&#x268${(parseInt(parsedData.die_2) - 1)}; `;

      _this.dice.html(diceEntities);
      $(_this.recentBetsSelector).show();

      let recentBet = `
        <tr>
          <td>${parsedData.guess}</td>
          <td>${parsedData.roll}</td>
          <td class="text-warning">
            <i class="fas fa-fw fa-database"></i> ${parsedData.wagered}
          </td>
          <td>${parseFloat(parsedData.payout)}x</td>
          <td class="text-${betClass}">
            <i class="fas fa-fw fa-database"></i> ${parsedData.net}
          </td>
        </tr>
      `;
      let recentBetCount = $(`${_this.recentBetsSelector} tr`).length;

      $(`${_this.recentBetsSelector} tbody`).prepend(recentBet);
      if (recentBetCount > 10) {
        $(`${_this.recentBetsSelector} tr:last`).remove();
      }

      return _this.outcomeStatus.addClass(`small alert alert-${alertClass}`)
        .html(statusHTML);
    }).fail(function (xhr, status, error) {
      let statusClass = 'alert-danger';
      let errorMessage = 'You are out of coins. You should buy more.';

      if (xhr.responseJSON) {
        errorMessage = xhr.responseJSON.error;
      } else if (error == 'TOO MANY REQUESTS') {
        errorMessage = 'You have been temporarily rate limited.';
      }

      return _this.outcomeStatus.addClass(statusClass).text(errorMessage);
    }).always(function (xhr, status, error) {
      _this.spinner.hide();
      _this.container.find('button').prop('disabled', false);
      _this.outcomeStatus.show();

      return xhr;
    });
  }
};
