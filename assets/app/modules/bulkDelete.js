import pluralize from 'modules/pluralize';

export default class BulkDelete {
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
    this.selectAll = '#select_all';
    this.checkedItems = '.js-checkbox-item';
    this.colheader = '.js-col-header';
    this.selectedRow = 'warning';
    this.updateScope = '#scope';
  }

  attachEvents() {
    let _this = this;

    $('body').on('change', this.checkedItems, function () {
      let checkedSelector = `${_this.checkedItems}:checked`;
      let itemCount = $(checkedSelector).length;
      let pluralizeItem = pluralize('item', itemCount);
      let scopeOptionText = `${itemCount} selected ${pluralizeItem}`;

      if ($(this).is(':checked')) {
        $(this).closest('tr').addClass(_this.selectedRow);

        $(_this.colheader).hide();
        _this.container.show();
      }
      else {
        $(this).closest('tr').removeClass(_this.selectedRow);

        if (itemCount === 0) {
          _this.container.hide();
          $(_this.colheader).show();
        }
      }

      $(`${_this.updateScope} option:first`).text(scopeOptionText);
    });

    $('body').on('change', this.selectAll, function () {
      let checkedStatus = this.checked;

      $(_this.checkedItems).each(function () {
        $(this).prop('checked', checkedStatus);
        $(this).trigger('change');
      });
    });
  }
};
