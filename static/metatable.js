// vim: set sw=2 foldmethod=marker :
function create_metatable($table) { // {{{
  $table.$head = $table.children('thead').first();
  $table.$body = $table.children('tbody').first();
  function create_metacell() {
    var $metacell =  $('<div />').addClass('metacell')
      .addClass('ritz'); // "ritz" is expected by google CSS
    $metacell.$scroller = $('<div />').addClass('scroller')
      .appendTo($metacell);
    $metacell.$pager = $('<div />').addClass('pager')
      .appendTo($metacell.$scroller);
    $metacell.$table = $($table[0].cloneNode())
      .appendTo($metacell.$pager);
    $metacell.$table.$head = $($table.$head[0].cloneNode())
      .appendTo($metacell.$table);
    $metacell.$table.$body = $($table.$body[0].cloneNode())
      .appendTo($metacell.$table);
    return $metacell;
  }
  var $FF = create_metacell().addClass('frozen-rows frozen-columns');
  var $FM = create_metacell().addClass('frozen-rows moving-columns');
  var $MF = create_metacell().addClass('moving-rows frozen-columns');
  var $MM = create_metacell().addClass('moving-rows moving-columns');
  var $AA = $('<table />').addClass('metatable')
    .append( $('<tr />').append($FF, $FM), $('<tr />').append($MF, $MM) );

  const frozenborder = 3; /* sync with metatable.css */

  { // clone head row {{{
    var $headrow = $table.$head.children('tr').first();
    var $corner = $headrow.children('th:first-child');
    var $headrow$moving = $($headrow[0].cloneNode()).append($corner.clone());
    var $header$frozen = $headrow.children('th.frozen-column-cell').first();
    var $headers$moving
    if ($header$frozen.length > 0) {
      $headers$moving = $header$frozen.nextAll();
    } else {
      $headers$moving = $corner.nextAll();
    }
    $headrow$moving.append($headers$moving);
    $header$frozen.remove();
    $FF.$table.$head.append($headrow);
    $MF.$table.$head.append($headrow.clone());
    $FM.$table.$head.append($headrow$moving);
    $MM.$table.$head.append($headrow$moving.clone());
  } // }}}

  { // clone rows {{{
    var $row$frozen =
      $table.$body.children('tr:has(th.freezebar-horizontal-handle)').first();
    var $rows$moving;
    if ($row$frozen.length > 0) {
      $rows$moving = $row$frozen.nextAll('tr');
    } else {
      $rows$moving = $table.$body.children('tr');
    }
    $rows$moving.each(function() {
      split_row($(this), $MF.$table.$body, $MM.$table.$body);
    });
    $row$frozen.remove()
    $table.$body.children('tr').each(function() {
      split_row($(this), $FF.$table.$body, $FM.$table.$body);
    });
    function split_row($row, $Fbody, $Mbody) {
      var $cell$frozen = $row.children('td.freezebar-cell').first();
      var $cells$moving;
      if ($cell$frozen.length > 0) {
        $cells$moving = $cell$frozen.nextAll();
      } else {
        $cells$moving = $row.children('td');
      }
      var $row$moving = $($row[0].cloneNode())
        .append($row.children('th:first-child').clone())
        .append($cells$moving);
      $cell$frozen.remove();
      $Fbody.append($row);
      $Mbody.append($row$moving);
    }
  } // }}}

  $AA.resize = function() {
    var frozenwidth = $FF.$table.width();
    var frozenheight = $FF.$table.height()
    var viewwidth = $(window).width();
    var viewheight = $(window).height();
    var displayfrozenwidth = Math.min(frozenwidth, viewwidth / 2.0);
    var displayfrozenheight = Math.min(frozenheight, viewheight / 2.0);
    var displaymainwidth = viewwidth - Math.min(frozenwidth, viewwidth / 2.0) - frozenborder;
    var displaymainheight = viewheight - Math.min(frozenheight, viewheight / 2.0) - frozenborder;
    $FF.$scroller.css({width: displayfrozenwidth, height: displayfrozenheight});
    $FM.$scroller.css({width: displaymainwidth,   height: displayfrozenheight});
    $MF.$scroller.css({width: displayfrozenwidth, height: displaymainheight});
    $MM.$scroller.css({width: displaymainwidth,   height: displaymainheight});
  }
  $(window).resize($AA.resize);

  $MM.$scroller.scroll(function() {
    var MM_table_position = $MM.$table.position();
    var MM_scroller_position = $MM.$scroller.position();
    $MF.$table.css({'top' : MM_table_position.top - MM_scroller_position.top});
    $FM.$table.css({'left' : MM_table_position.left - MM_scroller_position.left});
  });

  $MF.$scroller.scroll(function() {
    var MF_table_position = $MF.$table.position();
    var MF_scroller_position = $MF.$scroller.position();
    $FF.$table.css({'left' : MF_table_position.left - MF_scroller_position.left});
  });

  $FM.$scroller.scroll(function() {
    var FM_table_position = $FM.$table.position();
    var FM_scroller_position = $FM.$scroller.position();
    $FF.$table.css({'top' : FM_table_position.top - FM_scroller_position.top});
  });

  return $AA;

} // }}}

