
function social_rel(graph, elid, width, height) {
    //var width = 800, height = 500;
    var color = d3.scale.category20();
    var radius = d3.scale.sqrt()
        .range([0, 6]);

    var svg = d3.select(elid).append("svg")
        .attr("width", width)
        .attr("height", height);

    var force = d3.layout.force()
        .size([width, height])
        .charge(-900)
        .linkDistance( 130 );

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


    svg.append("defs").selectAll("marker")
        .data(["type1", "type2", "type3"])
        .enter().append("marker")
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", 0)
        .attr("markerWidth", 7)
        .attr("markerHeight", 7)
        .attr("orient", "auto")
        .attr("fill","#ffffff")
        .append("path")
        .attr("d", "M0,-5L5,0L0,6");

    var path = svg.append("g").selectAll("path")
        .data(force.links())
        .enter().append("path")
        .attr("class", function(d) { return "link " + d.type; })
        .attr("marker-end", function(d) { return "url(#" + d.type + ")"; })
        .style("stroke-width", function(d) { return Math.sqrt(8); });

    var node = svg.append("g").selectAll("circle")
        .data(force.nodes())
        .enter().append("g")
        .attr("class", "node")
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })
        .call(force.drag);

        node.append("defs")
        .append('mask')
        .attr("id", "mask_pic")
        .append("circle")
        .attr("r", function(d) { return radius(15); })
        .style("fill", "#ffffff");

        node.append('image')
        .attr("xlink:href", function(d) { return d.gravatar_url; })
        .attr("mask", "url(#mask_pic)")
        .attr("x", -25)
        .attr("y", -25)
        .attr("width", 50)
        .attr("height", 50);

        node.append("text")
        .attr("dy", 35)
        .attr("text-anchor", "middle")
        .style("font-size", '12px')
        .style("fill", '#ffffff')
        .text(function(d) { return d.name; });

    function tick() {
        node.attr("transform", function(d) {
            if (d.index == 0){
                return "translate( 50, 50)";
            }else{
                return "translate(" + d.x + "," + d.y + ")";
            }
        });

        path.attr("d", function(d) {
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
        });

    }


}
