function activePos(me, who, detail, xhr){
    var id = 'social-graph-'+who;

    $("#"+id).empty();
    detail.children().find(".loader").show();

    detail.addClass("pos");
    detail.fadeIn();

    var odd = detail.attr('odd');
    var query = me + "," + who;
    var color = "#1abc9c";
    if (odd % 2 == 0){ color =  "#f1c40f"; }

    if(xhr && xhr.readyState != 4){
      $("#"+id).empty();
      detail.children().find(".loader").show();
      xhr.abort();
    }
    xhr = $.ajax({
      type: "GET",
      url: "/social.json?users=" + query,
      success: function(result, status, xhr) {
          detail.children().find(".loader").fadeOut();
          $("#"+id).css("background-color", color);

          var width = $("#"+id).width();
          var height = 500;

          social_rel(result, '#' + id, width, height);
      },
    });
}

function initialize(me, query) {
    var xhr_socialmap;
    var xhr_task;
    $('#query').val(query);
    $(".task").on("click", function(d){
        var task = $(this);
        var who = $(this).attr('id').split("-")[1];
        var detail = $(this).parent().find("#detail-"+who);
        var has_pos = detail.hasClass("pos")

        $(".pos").animate(
            { height: 0, opacity: 0 },
            'slow',
            function() {
                $(this).attr("style","display:none");
                $(this).removeClass("pos");
                task.ScrollTo();
                }
        );

        if (!has_pos){
            task.ScrollTo({
                callback: function(){
                    activePos(me, who, detail, xhr_task);
                }
            });
        }

    });

    $("#social_map").on("click",function(d){
        var users = $(".task-userid a").map(function() {return $(this).text()});
        users = $.makeArray(users);
        users.unshift('{{me}}');
        var id = "social-map";

        if(xhr_socialmap && xhr_socialmap.readyState != 4){
          xhr_socialmap.abort();
        }
        xhr_socialmap = $.ajax({
          type: "GET",
          url: "/social.json?users=" + users,
          success: function(result, status, xhr) {
          $("#"+id).css("background-color", "black");
              var width = $("#"+id).width();
              var height = 500;

              social_rel(result, '#' + id, width, height);
          },
        });
    });
}

function onClickMore() {
    // TODO
}
