"use strict";

var vm = require('vm');

var contexts = {};

var error = function(name, message) {
  return {name: name, message: message};
};

var create_requirements_obj = function(requirements) {
  var o = {};
  requirements.forEach(function(val){
    var name, lib;
    if(val.isList()) {
      name = val[0];
      lib = require(val[1]);
    } else {
      name = val;
      lib = require(val);
    }
    o[name] = lib;
  });
  return o;
};

var basic_context_obj = function(){
  return {
    global: global,
    require: require,
    setTimeout: setTimeout,
    setInterval: setInterval,
    clearInterval: clearInterval,
    clearTimeout: clearTimeout,
    console: console
  }
};

// extend the obj (first parameter)
var extend = function(obj) {
  // for each other parameter
  Array.prototype.forEach.call(Array.prototype.slice.call(arguments, 1), function(source) {
    // loop through all properties of the other objects
    for (var prop in source) {
      // if the property is not undefined then add it to the object.
      if (source[prop] !== void 0) obj[prop] = source[prop];
    }
  });
  // return the object (first parameter)
  return obj;
};


var create_context = function(requirements) {
  var req = create_requirements_obj(requirements || []);
  var ctx = extend(req, basic_context_obj())
  return vm.createContext(ctx);
};

module.exports.mkcontext = function(data, resp) {
  if (!data.name) {
    resp(error("Argument","Missing required argument data"), "err");
    return;
  }

  if(!data.requirements) {
    data.requirements = [];
  }

  contexts[data.name] = create_context(data.requirements);
  return resp(data.name);
}

module.exports.eval = function(data, resp) {
  if(!data.code) {
    resp(error("Argument", "Missing required argument code"), "err");
    return
  }

  var script;
  try {
    script = vm.createScript(data.code);
  } catch (ex) {
    resp(ex, "err");
    return;
  }

  var context;

  if(data.context) {
    context = contexts[data.context];
    if(!context) {
      resp(error("Runtime", "No context named" + data.context), "err");
      return;
    }
  } else {
    context = create_context()
  }


  try {
    var res = script.runInContext(context);
    resp(res);
    return;
  } catch (ex) {
    resp(ex, "err");
    return;
  }

}

