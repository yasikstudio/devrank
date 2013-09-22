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

    $(".social-progress").hide();
    $("#social_map").on("click",function(d){
        var id = "social-map-content";
        var toggle = $(this).hasClass("toggle");

        if (toggle == false){
            $(".social-progress").show();
            $("#"+id).show();
            $(this).toggleClass("toggle");
            $(this).text("Back");
            $("#search_form").hide();

            var users = $(".task-userid a").map(function() {return $(this).text()});
            users = $.makeArray(users);
            users.unshift('{{me}}');

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
                          social_rel(result, '#' + id, width, height);
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
                    $("#"+id).empty();
                    $("#"+id).hide();
                }
            );
        }

    });
}

function removeMoreButton() {
    $("#moreButton").html("<div>no more data</div>");
}

function onClickMore(me, query) {
    var USERS_PER_PAGE = 20;
    var count = $(".task-userid a").size();
    if (count % USERS_PER_PAGE != 0) {
        removeMoreButton();
        alert('Error: no more data...');
    } else {
        var page = (count / 20) + 1;
        $.ajax({
            url: '/search?' + $.param({m: me, q: query, p: page})
        }).done(function(data) {
            $("#result_list_data").append(data);
            var newCount = $(".task-userid a").size();
            if (count == newCount) {
                removeMoreButton();
            }
        });
    }
}
