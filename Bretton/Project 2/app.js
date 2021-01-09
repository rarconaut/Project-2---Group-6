//Load data from data.csv
console.log("Hello World");

d3.json("combined-data.json").then(function (Data) {

  var data = Data;

  var Data_2015 = Data.filter(Data => (Data.report_year === "2015"));
  var Data_2016 = Data.filter(Data => (Data.report_year === "2016"));
  var Data_2017 = Data.filter(Data => (Data.report_year === "2017"));
  var Data_2018 = Data.filter(Data => (Data.report_year === "2018"));
  var Data_2019 = Data.filter(Data => (Data.report_year === "2019"));
  var Data_2020 = Data.filter(Data => (Data.report_year === "2020"));

  console.log(Data_2015);


  var State_2015 = Data_2015.map(Data_2015 => Data_2015.state);
  var State_2016 = Data_2016.map(Data_2016 => Data_2016.state);
  var State_2017 = Data_2017.map(Data_2017 => Data_2017.state);
  var State_2018 = Data_2018.map(Data_2018 => Data_2018.state);
  var State_2019 = Data_2019.map(Data_2019 => Data_2019.state);
  var State_2020 = Data_2020.map(Data_2020 => Data_2020.state);

  //Remove Duplicate State Entries
  var distinct_states_15 = [];
  for (var i = 0; i < State_2015.length; i++) {
    var str = State_2015[i];
    if (distinct_states_15.indexOf(str) == -1) {
      distinct_states_15.push(str);
    }
  };


  var distinct_states_16 = [];
  for (var i = 0; i < State_2016.length; i++) {
    var str = State_2016[i];
    if (distinct_states_16.indexOf(str) == -1) {
      distinct_states_16.push(str);
    }
  };

  var distinct_states_17 = [];
  for (var i = 0; i < State_2017.length; i++) {
    var str = State_2017[i];
    if (distinct_states_17.indexOf(str) == -1) {
      distinct_states_17.push(str);
    }
  };

  var distinct_states_18 = [];
  for (var i = 0; i < State_2018.length; i++) {
    var str = State_2018[i];
    if (distinct_states_18.indexOf(str) == -1) {
      distinct_states_18.push(str);
    }
  };

  var distinct_states_19 = [];
  for (var i = 0; i < State_2019.length; i++) {
    var str = State_2019[i];
    if (distinct_states_19.indexOf(str) == -1) {
      distinct_states_19.push(str);
    }
  };

  var distinct_states_20 = [];
  for (var i = 0; i < State_2020.length; i++) {
    var str = State_2020[i];
    if (distinct_states_20.indexOf(str) == -1) {
      distinct_states_20.push(str);
    }
  };
  console.log(distinct_states_16);

  var market_caps=[];
  
  var caps_2015 = State_2015.filter(State_2015 => (State_2015.state === distinct_states_15[0]));
  
  //states_2015.foreach(([state,cap])=>{
  //  var state=Data_2015.state;
  //  var cap=Data_2015.market_cap;
    
  //  if (state=distinct_states_15[0]){1
  //    distinct_states_15.push(cap)

  var distinct_states_20 = [];
  for (var i = 0; i < State_2020.length; i++) {
    var str = State_2020[i];
    if (distinct_states_20.indexOf(str) == -1) {
      distinct_states_20.push(str);
    }
  };
  console.log(distinct_states_15);
  console.log(distinct_states_15[10]);

});
    


