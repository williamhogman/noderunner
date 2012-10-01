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

var create_context = function(requirements) {
  return vm.createContext(create_requirements_obj(requirements))
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
    context = vm.createContext({"require": require});
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

