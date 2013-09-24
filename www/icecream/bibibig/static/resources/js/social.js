function social_rel(graph, elid, width, height, mode) {
    //* mode false is social_map mode.

    var radius = d3.scale.sqrt()
        .range([0, 6]);

    var svg = d3.select(elid).append("svg")
        .attr("width", width)
        .attr("height", height);

    var force = d3.layout.force()
        .size([width, height]);

        if (mode == false){
          force.gravity(1)
          .charge(-4000)
          .linkDistance( 200 );
        }else if (mode == true){
          force.gravity(0.05)
          .charge(-2000)
          .linkDistance( 100 );
        }

    var nodes = {};
    graph.links.forEach(function(link) {
        link.source = nodes[link.source] || (nodes[link.source] = {name: link.source, gravatar_url: link.src_gravatar_url });
        link.target = nodes[link.target] || (nodes[link.target] = {name: link.target, gravatar_url: link.tgt_gravatar_url });
    });

    force
        .nodes(d3.values(nodes))
        .links(graph.links)
        .on("tick", tick)
        .start();

    var path = svg.append("g").selectAll("path")
        .data(force.links())
        .enter().append("path")
        if (mode == false){
          path.attr("class", function(d) { return "link type1"; });
        }else if (mode == true){
          path.attr("class", function(d) { return "link type2"; });
        }

    var node = svg.append("g").selectAll("circle")
        .data(force.nodes())
        .enter().append("g")
        .attr("class", "node")
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })
        .call(force.drag);

        node.append('mask')
        .attr("id", "mask_pic")
        .append("circle")
        .attr("r", function(d) { return radius(20); })
        .style("fill", "#ffffff");

        node.append('image')
        .attr("xlink:href", function(d) { return d.gravatar_url; })
        .attr("mask", "url(#mask_pic)")
        .attr("x", -30)
        .attr("y", -30)
        .attr("width", 60)
        .attr("height", 60);

        node.append("text")
        .attr("dy", 35)
        .attr("text-anchor", "middle")
        .style("font-size", '12px')
        .style("fill", '#ffffff')
        .text(function(d) { return d.name; });

    function tick() {
        node.attr("transform", function(d) {
            if (mode == true){
                if (d.index == 0){
                    return "translate( 50, 50)";
                }else{
                    return "translate(" + d.x + "," + d.y + ")";
                }
            }else{
                return "translate(" + d.x + "," + d.y + ")";
            }
        });

        path.attr("d", function(d) {
            if (mode == true){
                if (d.source.index == 0){
                    d.source.x=50;
                    d.source.y=50;
                    var dx = d.target.x - d.source.x,
                    dy = d.target.y - d.source.y;
                    return "M" + d.source.x + "," + d.source.y + "A0,0 0 0,1 " + d.target.x + "," + d.target.y;
                }else{
                    var dx = d.target.x - d.source.x,
                    dy = d.target.y - d.source.y;
                    return "M" + d.source.x + "," + d.source.y + "A0,0 0 0,1 " + d.target.x + "," + d.target.y;
                }
            }else{
                var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y;
                return "M" + d.source.x + "," + d.source.y + "A0,0 0 0,1 " + d.target.x + "," + d.target.y;
            }
        });

    }

}
