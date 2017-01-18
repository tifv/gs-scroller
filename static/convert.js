// vim: set sw=2 foldmethod=marker :
function split_and_rock(table) {
  function clone_table(table) {
    var clone = $(table[0].cloneNode());
    clone
      .append( $(table.find('thead')[0].cloneNode())
        .append( $(table.find('thead > tr')[0].cloneNode())
          .append( $(table.find('thead > tr > th:first-child')[0].cloneNode())
          )
        )
      );
    clone
      .append( $(table.find('tbody')[0].cloneNode()) );
    return clone;
  }
  function fillin(section, table) {
    $('<div class="scroller"></div>').appendTo(section)
      .append(table);
  }
  var FF = $('<td></td>'), FF_table = clone_table(table); fillin(FF, FF_table);
  var FM = $('<td></td>'), FM_table = clone_table(table); fillin(FM, FM_table);
  var FA = $('<tr></tr>');
  var MF = $('<td></td>'), MF_table = clone_table(table); fillin(MF, MF_table);
  var MM = $('<td></td>'), MM_table = clone_table(table); fillin(MM, MM_table);
  var MA = $('<tr></tr>');
  var AA = $('<table class="ritz"></table>'); // ritz is expected by google CSS
  FA.append(FF, FM);
  MA.append(MF, MM);
  AA.append(FA, MA);

  const frozenborder = 3;
  const frozenbordercss = frozenborder + 'px solid #dadfe8';
  AA.css({'border': 0, 'padding': 0, 'border-collapse': 'collapse'});
  AA.find('td:has(.scroller)').css({'padding' : 0});
  AA.find('tr:first-child > td:has(.scroller)').css({'border-bottom': frozenbordercss});
  AA.find('tr > td:first-child:has(.scroller)').css({'border-right': frozenbordercss});

  var FF_scroller = FF.find('.scroller');
  var FM_scroller = FM.find('.scroller');
  var MF_scroller = MF.find('.scroller');
  var MM_scroller = MM.find('.scroller');

  table.detach();
  $('body').empty();

  { // clone headrow {{{
    var frozen_column_reached = false;
    var FF_headrow = FF_table.find('thead > tr');
    var FM_headrow = FM_table.find('thead > tr');
    var MF_headrow = MF_table.find('thead > tr');
    var MM_headrow = MM_table.find('thead > tr');
    table.find('thead > tr > th:not(:first-child)').each(function (i) {
      if ($(this).hasClass('frozen-column-cell')) {
        frozen_column_reached = true;
        return;
      }
      if (!frozen_column_reached) {
        $(this).clone().appendTo(FF_headrow);
        $(this).clone().appendTo(MF_headrow);
      } else {
        $(this).clone().appendTo(FM_headrow);
        $(this).clone().appendTo(MM_headrow);
      }
    });
  } // }}}

  { // clone rows {{{
    var frozen_row_reached = false;
    var FF_body = FF_table.find('tbody');
    var FM_body = FM_table.find('tbody');
    var MF_body = MF_table.find('tbody');
    var MM_body = MM_table.find('tbody');
    table.find('tbody > tr').each(function (i) {
      if ($(this).find('th.freezebar-horizontal-handle').length > 0) {
        frozen_row_reached = true;
        return;
      }
      var th = $(this).find('th:first-child');
      var AF_row, AM_row;
      if (!frozen_row_reached) {
        //AF_row = $(this.cloneNode()).append(th.clone()).appendTo(FF_body);
        AF_row = $(this).appendTo(FF_body);
        AM_row = $(this.cloneNode()).append(th.clone()).appendTo(FM_body);
      } else {
        //AF_row = $(this.cloneNode()).append(th.clone()).appendTo(MF_body);
        AF_row = $(this).appendTo(MF_body);
        AM_row = $(this.cloneNode()).append(th.clone()).appendTo(MM_body);
      }
      var frozen_col = $(this).find('td.freezebar-cell');
      frozen_col.nextAll('td').appendTo(AM_row);
      frozen_col.remove();
    });
  } // }}}

  $('body').append(AA);

  FF_scroller.css({'overflow-x' : 'hidden', 'overflow-y' : 'hidden'});
  FM_scroller.css({'overflow-x' : 'hidden', 'overflow-y' : 'scroll'});
  MF_scroller.css({'overflow-x' : 'scroll', 'overflow-y' : 'hidden'});
  MM_scroller.css({'overflow-x' : 'scroll', 'overflow-y' : 'scroll'});
  function resize() {
    var frozenwidth = FF_table.width();
    var frozenheight = FF_table.height()
    var viewwidth = $(window).width();
    var viewheight = $(window).height();
    var displayfrozenwidth = Math.min(frozenwidth, viewwidth / 2.0);
    var displayfrozenheight = Math.min(frozenheight, viewheight / 2.0);
    var displaymainwidth = viewwidth - Math.min(frozenwidth, viewwidth / 2.0) - frozenborder;
    var displaymainheight = viewheight - Math.min(frozenheight, viewheight / 2.0) - frozenborder;
    FF_scroller.css({width: displayfrozenwidth, height: displayfrozenheight});
    FM_scroller.css({width: displaymainwidth, height: displayfrozenheight});
    MF_scroller.css({width: displayfrozenwidth, height: displaymainheight});
    MM_scroller.css({width: displaymainwidth, height: displaymainheight});
  }
  $(window).resize(resize);
  resize();

  MM.find('.scroller').scroll(function() {
    var MM_table_position = MM_table.position();
    var MM_scroller_position = MM_scroller.position();
    MF_table.css({'margin-top' : MM_table_position.top - MM_scroller_position.top});
    FM_table.css({'margin-left' : MM_table_position.left - MM_scroller_position.left});
  });

  MF.find('.scroller').scroll(function() {
    var MF_table_position = MF_table.position();
    var MF_scroller_position = MF_scroller.position();
    FF_table.css({'margin-left' : MF_table_position.left - MF_scroller_position.left});
  });

  FM.find('.scroller').scroll(function() {
    var FM_table_position = FM_table.position();
    var FM_scroller_position = FM_scroller.position();
    FF_table.css({'margin-top' : FM_table_position.top - FM_scroller_position.top});
  });

}

