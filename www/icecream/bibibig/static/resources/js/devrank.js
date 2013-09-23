function activePos(me, who, detail){
    var id = 'social-graph-'+who;

    $("#"+id).empty();
    detail.children().find(".loader").show();

    detail.addClass("pos");
    detail.fadeIn();

    var odd = detail.attr('odd');
    var query = me + "," + who;
    var color = "#1abc9c";
    if (odd % 2 == 0){ color =  "#f1c40f"; }

    var xhr = $.ajax({
      type: "GET",
      url: "/social.json?users=" + query,
      success: function(result, status, xhr) {
          detail.children().find(".loader").fadeOut();
          $("#"+id).css("background-color", color);

          var width = $("#"+id).width();
          var height = 500;

          social_rel(result, '#' + id, width, height, true);
      },
    });
}

function boundEvents(me, query) {
    $(".task:not(.bound-click)").addClass('bound-click').on("click", function(d){
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
                    activePos(me, who, detail);
                }
            });
        }

    });
}

function initialize(me, query) {
    $("#moreButton-alert").hide();
    var xhr_socialmap;
    $('#query').val(query);
    boundEvents(me, query);

    $(".social-progress").hide();
    $("#social_map").on("click",{ me : "{{me}}"}, function(d){
        var id = "social-map-content";
        var draw = ".social-map-draw";
        var toggle = $(this).hasClass("toggle");

        if (toggle == false){
            $(".social-progress").show();
            $("#"+id).show();
            $(this).toggleClass("toggle");
            $(this).text("Back");
            $("#search_form").hide();

            var users = $(".task-userid a").map(function() {return $(this).text()});
            users = $.makeArray(users);
            users.unshift(me);

            if(xhr_socialmap && xhr_socialmap.readyState != 4){
              xhr_socialmap.abort();
            }

            var width = $( window ).width();
            var height = $( window ).height() - $(".navbar").height();
            $("#"+id).animate(
                { height: height },
                'slow',
                function() {
                    xhr_socialmap = $.ajax({
                      type: "GET",
                      url: "/social.json?users=" + users,
                      success: function(result, status, xhr) {
                          $(".social-progress").hide();
                          social_rel(result, draw, width, height, false);
                      },
                    });
                }
            );
        }else{
            if(xhr_socialmap){
                $(".social-progress").hide();
              xhr_socialmap.abort();
            }
            $(this).toggleClass("toggle");
            $(this).text("Social Map");
            $("#search_form").show();

            $("#"+id).animate(
                { height: 0 },
                'slow',
                function() {
                    $(draw).empty();
                    $("#"+id).hide();
                }
            );
        }

    });
}

function removeMoreButton() {
    $("#moreButton").fadeOut();
    $("#moreButton-alert").fadeIn();
}

function onClickMore(me, query) {
    var USERS_PER_PAGE = 20;
    var count = $(".task-userid a").size();
    if (count % USERS_PER_PAGE != 0) {
        removeMoreButton();
    } else {
        var page = (count / 20) + 1;
        $.ajax({
            url: '/search?' + $.param({m: me, q: query, p: page})
        }).done(function(data) {
            $("#result_list_data").append(data);
            boundEvents(me, query);
            var newCount = $(".task-userid a").size();
            if (count == newCount) {
                removeMoreButton();
            }
        });
    }
}
