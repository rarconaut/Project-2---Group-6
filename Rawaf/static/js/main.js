// Plot.ly Homework - Belly Button Biodiversity

// Initialize Dashboard with default dataset
function init() {
  // Select the input value from the drop down menu
  var dropdownMenu = d3.select("#selDataset");
  // console.log(dropdownMenu);

  // Create menu options from json 'names' data 
  d3.json("../../samples.json").then(function (navelData) {
    var nameIDs = navelData.names;
    // console.log(nameIDs);

    nameIDs.forEach(function (id) {
      return dropdownMenu
        .append("option")
        .attr("value", id)
        .text(id);
    });

    // Build the initial plots/metadata with the first sample
    var defaultSample = nameIDs[0];
    console.log(defaultSample);

    grabMeta(defaultSample);
    buildPlots(defaultSample);
  });
}

// Call the init function to start the page
init()

//  Drop down menu hanlder
function optionChanged() {
  // Select input value from drop down menu
  var dropdownMenu = d3.select("#selDataset");
  var dataset = dropdownMenu.node().value;
  console.log(dataset);

  // Build plots/grab metadata with the new sample
  grabMeta(dataset);
  buildPlots(dataset);
}

function grabMeta(dataset) {
  // Access json data
  d3.json("../../samples.json").then(function (navelData) {

    // Grab metadata from the json object
    var sampleMeta = navelData.metadata.filter(sample => sample.id == dataset)[0];
    console.log(sampleMeta);

    // Clear any previous metadata value before displaying current
    displayMeta = d3.select("#sample-metadata");
    displayMeta.html("");

    // Use `Object.entries` and `forEach` to iterate through keys and values
    Object.entries(sampleMeta).forEach(([key, value]) => {
      console.log(`Key: ${key} and Value ${value}`)

      displayMeta
        .append("p")
        .text(`${key}: ${value}`)
    });
  });
}

function buildPlots(dataset) {

  d3.json("../../samples.json").then(function (data) {
    // Grab values from the response json object to build the plots
    var selectedSample = data.samples.filter(sample => sample.id === dataset)[0];

    var sampleValues = selectedSample.sample_values.slice(0, 10)
    var otuIDs = selectedSample.otu_ids.slice(0, 10);
    var otuLabels = selectedSample.otu_labels.slice(0, 10);

    // Print the names of the columns
    console.log(dataset)
    // console.log(sampleValues, otuIDs, otuLabels);

    // The horizonal bar graph
    var barh = {
      type: "bar",
      orientation: "h",
      x: sampleValues,
      y: otuIDs
    }

    var data = [barh];

    var layout = {
      title: `Navel Biodiversity for Subject ${dataset}`,
      xaxis: {
        title: "Sample Values",
      },
      yaxis: {
        title: "OTU IDs"
      }
    };

    Plotly.newPlot("bar", data, layout);

    // The bubble chart
    var bubble = {
      type: "scatter",
      mode: "markers",
      text: otuLabels,
      x: otuIDs,
      y: sampleValues,
      marker: {
        color: otuIDs,
        size: sampleValues
      }
    }

    var data = [bubble];

    var layout = {
      title: `Navel Biodiversity for Subject ${dataset}`,
      xaxis: {
        title: "OTU IDs",
      },
      yaxis: {
        title: "Sample Values"
      }
    };

    Plotly.newPlot("bubble", data, layout);

  });
}