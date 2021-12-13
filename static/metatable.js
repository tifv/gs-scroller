function create_metatable($table) { // {{{1
  $table.$head = $table.children('thead').first();
  $table.$body = $table.children('tbody').first();

  function create_metacell() { // {{{
    var $metacell =  $('<td />')
      .addClass('metatable__cell')
      .addClass('ritz'); // "ritz" is expected by google CSS
    $metacell.$scroller = $('<div />')
      .addClass('metatable__scroller')
      .appendTo($metacell);
    $metacell.$pager = $('<div />')
      .addClass('metatable__pager')
      .appendTo($metacell.$scroller);
    $metacell.$table = $($table[0].cloneNode())
      .appendTo($metacell.$pager);
    $metacell.$table.$head = $($table.$head[0].cloneNode())
      .appendTo($metacell.$table);
    $metacell.$table.$body = $($table.$body[0].cloneNode())
      .appendTo($metacell.$table);
    return $metacell;
  } // }}}

  var
    $FF = create_metacell(), $FM = create_metacell(),
    $MF = create_metacell(), $MM = create_metacell();
  var
    $FA = $FF.add($FM).addClass('metatable__cell--frozen-rows'),
    $AF = $FF.add($MF).addClass('metatable__cell--frozen-cols'),
    $MA = $MF.add($MM).addClass('metatable__cell--moving-rows'),
    $AM = $FM.add($MM).addClass('metatable__cell--moving-cols');
  var $AA = $('<table />').addClass('metatable')
    .append( $('<tr />').append($FA), $('<tr />').append($MA) );

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
      $AA.addClass('metatable--no-frozen-columns');
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
      $AA.addClass('metatable--no-frozen-rows');
    }
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
    $rows$moving.each(function() {
      split_row($(this), $MF.$table.$body, $MM.$table.$body);
    });
    $row$frozen.remove()
    $table.$body.children('tr').each(function() {
      split_row($(this), $FF.$table.$body, $FM.$table.$body);
    });
  } // }}}

  $AA.resize = function() { // {{{
    var dA = {
      width:  $(window).width(),
      height: $(window).height() };
    var b = {
      width:  parseInt($FF.css('border-right-width'),  10),
      height: parseInt($FF.css('border-bottom-width'), 10) };
    var F = {
      width:  Math.max($FF.$table.width(),  $MF.$table.width()),
      height: Math.max($FF.$table.height(), $FM.$table.height()) };
    /* var M = {
      width:  Math.max($FM.$table.width(),  $MM.$table.width()),
      height: Math.max($MF.$table.height(), $MM.$table.height()) }; */
    var dF = {
      width:  Math.min(F.width,  dA.width  / 2.0),
      height: Math.min(F.height, dA.height / 2.0) };
    var dM = {
      width:  dA.width  - dF.width  - b.width,
      height: dA.height - dF.height - b.height };
    $FF.$scroller.css({width: dF.width, height: dF.height});
    $FM.$scroller.css({width: dM.width, height: dF.height});
    $MF.$scroller.css({width: dF.width, height: dM.height});
    $MM.$scroller.css({width: dM.width, height: dM.height});
  } // }}}
  $(window).resize($AA.resize);

  $MM.$scroller.scroll(function() { // {{{
    var position = {
      left: $MM.$scroller.scrollLeft(),
      top:  $MM.$scroller.scrollTop() };
    $MF.$table.css({'top'  : -position.top});
    $FM.$table.css({'left' : -position.left});
  }); // }}}

  $MF.$scroller.scroll(function() { // {{{
    var position = {
      left: $MF.$scroller.scrollLeft() };
    $FF.$table.css({'left' : -position.left});
  }); // }}}

  $FM.$scroller.scroll(function() { // {{{
    var position = {
      top: $FM.$scroller.scrollTop() };
    $FF.$table.css({'top' : -position.top});
  }); // }}}

  function reconcile_rows($row1, $row2) {
    var height = Math.max($row1.height(), $row2.height());
    console.log("wow", height);
    $row1.css('height', height + "px");
    $row2.css('height', height + "px");
  }
  window.requestAnimationFrame(function() {
  window.requestAnimationFrame(function() {
    console.log("yeah");
    FFrows = $FF.$table.children('tbody').children().get();
    FMrows = $FM.$table.children('tbody').children().get();
    for (let i = 0; i < FFrows.length; ++i) {
      reconcile_rows($(FFrows[i]), $(FMrows[i]));
    }
    console.log("oh");
    MFrows = $MF.$table.children('tbody').children();
    MMrows = $MM.$table.children('tbody').children();
    console.log(MFrows);
    for (let i = 0; i < MFrows.length; ++i) {
      reconcile_rows($(MFrows[i]), $(MMrows[i]));
    }
    $AA.resize();
  })});

  return $AA;

}

