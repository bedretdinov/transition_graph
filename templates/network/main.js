function WheelLayout() {
    go.CircularLayout.call(this);
}

go.Diagram.inherit(WheelLayout, go.CircularLayout);
// override makeNetwork to set the diameter of each node and ignore the TextBlock label
WheelLayout.prototype.makeNetwork = function (coll) {
    var net = go.CircularLayout.prototype.makeNetwork.call(this, coll);
    net.vertexes.each(function (cv) {
        cv.diameter = 20;  // because our desiredSize for nodes is (20, 20)
    });
    return net;
}
// override commitNodes to rotate nodes so the text goes away from the center,
// and flip text if it would be upside-down
WheelLayout.prototype.commitNodes = function () {
    go.CircularLayout.prototype.commitNodes.call(this);
    this.network.vertexes.each(function (v) {
        var node = v.node;
        if (node === null) return;
        // get the angle of the node towards the center, and rotate it accordingly
        var a = v.actualAngle;
        if (a > 90 && a < 270) {  // make sure the text isn't upside down
            var textBlock = node.findObject("TEXTBLOCK");
            textBlock.angle = 180;
        }
        node.angle = a;
    });
};
// override commitLinks in order to make sure all of the Bezier links are "inside" the ellipse;
// this helps avoid links crossing over any other nodes
WheelLayout.prototype.commitLinks = function () {
    go.CircularLayout.prototype.commitLinks.call(this);
    if (this.network.vertexes.count > 4) {
        this.network.vertexes.each(function (v) {
            v.destinationEdges.each(function (de) {
                var dv = de.toVertex;
                var da = dv.actualAngle;
                var sa = v.actualAngle;
                if (da - sa > 180) da -= 360;
                else if (sa - da > 180) sa -= 360;
                //de.link.curviness = (sa > da) ? 15 : -15;
            })
        })
    }
}
// end WheelLayout class
var highlightColor = "red";  // color parameterization

if (window.goSamples) goSamples();  // init for these samples -- you don't need to call this
var $ = go.GraphObject.make;  // for conciseness in defining templates
window.myDiagram =
    $(go.Diagram, "myDiagramDiv", // must be the ID or reference to div
        {
            "toolManager.mouseWheelBehavior": go.ToolManager.WheelZoom,
            initialAutoScale: go.Diagram.Uniform,
            padding: 10,
            layout:
                $(WheelLayout,  // set up a custom CircularLayout
                    // set some properties appropriate for this sample
                    {
                        arrangement: go.CircularLayout.ConstantDistance,
                        nodeDiameterFormula: go.CircularLayout.Circular,
                        spacing: 120,
                        aspectRatio: 1,
                        sorting: go.CircularLayout.Optimized
                    }),
            isReadOnly: true,
            "undoManager.isEnabled": true,
            positionComputation: function (diagram, pt) {
                return new go.Point(Math.floor(pt.x), Math.floor(pt.y));
            },
            click: function (e) {  // background click clears any remaining highlighteds
                e.diagram.startTransaction("clear");
                e.diagram.clearHighlighteds();
                e.diagram.commitTransaction("clear");
            }
        });
// define the Node template
window.myDiagram.nodeTemplate =
    $(go.Node, "Horizontal",
        {
            selectionAdorned: false,
            locationSpot: go.Spot.Center,  // Node.location is the center of the Shape
            locationObjectName: "SHAPE",
            mouseEnter: function (e, node) {
                node.diagram.clearHighlighteds();
                node.linksConnected.each(function (l) {
                    highlightLink(l, true);
                });
                node.isHighlighted = true;
                var tb = node.findObject("TEXTBLOCK");
                if (tb !== null) tb.stroke = highlightColor;
            },
            mouseLeave: function (e, node) {
                node.diagram.clearHighlighteds();
                var tb = node.findObject("TEXTBLOCK");
                if (tb !== null) tb.stroke = "black";
            }
        },


        new go.Binding("text", "text"),  // for sorting the nodes
        $(go.Shape, "Ellipse",
            {
                name: "SHAPE",
                fill: "lightgray",  // default value, but also data-bound
                stroke: "transparent",  // modified by highlighting
                strokeWidth: 2,
                desiredSize: new go.Size(60, 60),
                portId: ""
            },  // so links will go to the shape, not the whole node
            new go.Binding("fill", "color"),
            new go.Binding("stroke", "isHighlighted",
                function (h) {
                    return h ? highlightColor : "transparent";
                })
                .ofObject()),
        $(go.TextBlock,
            {name: "TEXTBLOCK"},  // for search
            new go.Binding("text", "text"))
    );


function highlightLink(link, show) {
    link.isHighlighted = show;
    link.fromNode.isHighlighted = show;
    link.toNode.isHighlighted = show;
}

// define the Link template
window.myDiagram.linkTemplate =
    $(go.Link,
        {
            curve: go.Link.Bezier,
            adjusting: go.Link.Stretch,
            reshapable: true,
            selectionAdorned: false,
            mouseEnter: function(e, link) { highlightLink(link, true); },
            mouseLeave: function(e, link) { highlightLink(link, false); }
        },
        new go.Binding("points").makeTwoWay(),
        new go.Binding("curviness", "curviness"),
        $(go.Shape,
            new go.Binding("stroke", "color"),  // shape.stroke = data.color
            new go.Binding("strokeWidth", "thick")),  // shape.strokeWidth = data.thick
        $(go.Shape,
            {toArrow: "OpenTriangle", fill: null},
            new go.Binding("stroke", "color"),  // shape.stroke = data.color
            new go.Binding("strokeWidth", "thick")),  // shape.strokeWidth = data.thick
        $(go.Panel, "Auto",
            {cursor: "move"},  // visual hint that the user can do something with this link label
            new go.Binding("segmentOffset", "segmentOffset", go.Point.parse).makeTwoWay(go.Point.stringify)
        )
    );


function generateGraph(data) {
    preloader.hide()


    data = go.Model.fromJson(data);

    myDiagram.model = data


}


function initOneWayLine(data) {


      if(typeof window.myDiagram2!="undefined"){
          window.myDiagram2.model = go.Model.fromJson(data);
          return ''
      }


      var $ = go.GraphObject.make;  // for conciseness in defining templates

      window.myDiagram2 =
        $(go.Diagram, "myDiagramDiv2",  // must name or refer to the DIV HTML element
          {
            layout: $(go.ForceDirectedLayout),
            initialAutoScale: go.Diagram.Uniform,
              "toolManager.mouseWheelBehavior": go.ToolManager.WheelZoom,
            initialAutoScale: go.Diagram.Uniform,
            // isReadOnly: true,
            "undoManager.isEnabled": true,
          });


      // define the Node template
      window.myDiagram2.nodeTemplate =
        $(go.Node, "Auto",
          //new go.Binding("location", "loc", go.Point.parse).makeTwoWay(go.Point.stringify),
          // define the node's outer shape, which will surround the TextBlock
          $(go.Shape, "RoundedRectangle",
            {
              parameter1: 20,  // the corner has a large radius
              fill: $(go.Brush, "Linear", { 0: "rgb(51, 122, 183)", 1: "rgb(51, 122, 183)" }),
              stroke: "black",
              portId: "",
              fromLinkable: true,
              fromLinkableSelfNode: true,
              fromLinkableDuplicates: true,
              toLinkable: true,
              toLinkableSelfNode: true,
              toLinkableDuplicates: true,
              cursor: "pointer"
            }),
          new go.Binding("location", "loc", go.Point.parse),
          new go.Binding("fill", "color"),
          $(go.TextBlock,
            {
              stroke: "white",
              font: "bold 11pt helvetica, bold arial, sans-serif",
              editable: true  // editing the text automatically updates the model data
            },
            new go.Binding("text", "text").makeTwoWay())
        );

      // unlike the normal selection Adornment, this one includes a Button
      window.myDiagram2.nodeTemplate.selectionAdornmentTemplate =
        $(go.Adornment, "Spot",
          $(go.Panel, "Auto",
            $(go.Shape, { fill: null, stroke: "blue", strokeWidth: 2 }),
            $(go.Placeholder)  // this represents the selected Node
          ),
        ); // end Adornment


      // replace the default Link template in the linkTemplateMap
      window.myDiagram2.linkTemplate =
        $(go.Link,
          { curve: go.Link.Bezier, adjusting: go.Link.Stretch, reshapable: true },
          new go.Binding("points").makeTwoWay(),
          new go.Binding("curviness", "curviness"),
          $(go.Shape,
            new go.Binding("stroke", "color"),  // shape.stroke = data.color
            new go.Binding("strokeWidth", "thick")),  // shape.strokeWidth = data.thick
          $(go.Shape,
            { toArrow: "OpenTriangle", fill: null },
            new go.Binding("stroke", "color"),  // shape.stroke = data.color
            new go.Binding("strokeWidth", "thick")),  // shape.strokeWidth = data.thick
          $(go.Panel, "Auto",
            { cursor: "move" },  // visual hint that the user can do something with this link label
            new go.Binding("segmentOffset", "segmentOffset", go.Point.parse).makeTwoWay(go.Point.stringify)
          ),
            $(go.TextBlock, "transition",  // the label text
              {
                    //background: "black",
                    //stroke: "white",
                    textAlign: "center",
                    font: "12pt helvetica, arial, sans-serif",
                    margin: 4,
                    editable: true  // enable in-place editing
              },
              // editing the text automatically updates the model data
              new go.Binding("text").makeTwoWay()),
        );


      // read in the JSON-format data from the "mySavedModel" element
      window.myDiagram2.model = go.Model.fromJson(data);



      // jQuery(document).ready(function ($) {
      //     window.myDiagram2.addDiagramListener("ObjectSingleClicked", function (e, GraphObjec) {
      //               var part = e.subject.part;
      //               var code = ''
      //               for( k in myDiagram.model.nodeDataArray ){
      //                   if(myDiagram.model.nodeDataArray[k]['id']==part.$w){
      //                       code = myDiagram.model.nodeDataArray[k]['code']
      //                   }
      //               }
      //
      //               $.get('/point/{{type}}/{{date_from}}/{{date_to}}/'+code, initOneWayLine)
      //     });
      // });

}

jQuery(document).ready(function ($) {
    // $('#myDiagramDiv').height($(window).height() - $(window).height() * 0.5)
    // $('#myDiagramDiv2').height($(window).height() - $(window).height() * 0.5)
})