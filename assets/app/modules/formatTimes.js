import moment from 'moment';

export default class FormatTimes {
  constructor(fromNow, shortDate) {
    this.fromNowSelector = fromNow;
    this.shortDateSelector = shortDate;
    this.isAttached = false;
    this.attach();
  }

  attach() {
    if (this.isAttached) return;

    if ($(this.fromNowSelector).length === 0 && $(this.shortDateSelector).length === 0) {
      return;
    }

    this.attachUI();
    this.attachEvents();
    this.isAttached = true;
  }

  attachUI() {
    this.fromNow = $(this.fromNowSelector);
    this.shortDate = $(this.shortDateSelector);
  }

  attachEvents() {
    this.fromNow.each(function (i, e) {
      (function updateTime() {
        let time = moment($(e).data('datetime'));

        $(e).text(time.fromNow());
        $(e).attr('title', time.format('MMMM Do YYYY, h:mm:ss a Z'));

        setTimeout(updateTime, 1000);
      })();
    });

    this.shortDate.each(function (i, e) {
      let time = moment($(e).data('datetime'));

      $(e).text(time.format('MMM Do YYYY'));
      $(e).attr('title', time.format('MMMM Do YYYY, h:mm:ss a Z'));
    });
  }
};
