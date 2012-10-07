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
    if(Array.isArray(val)) {
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

var traverse_obj = function(obj, path){
  var tmp, ptr = obj;
  while(tmp = path.shift()) {
    ptr = ptr[tmp];
  }
  return ptr;
};

var get_context_global = function(context, name){
  var script = vm.createScript(name);
  return script.runInContext(context);
};

module.exports.get =  function(data, resp){
  var context;
  if(!data.context) {
    resp(error("Argument", "Missing required argument context"), "err");
    return;
  }

  context = contexts[data.context];
  if(!context) {
    resp(error("Argument", "No such context"), "err");
    return;
  }


  var path;
  if(!data.path) {
    resp(error("Argument", "Missing required argument path"), "err");
    return;
  }
  path = data.path;

  var first = path.shift();
  if(!first) {
    resp(error("Argument", "Invalid path argument"), "err");
    return;
  }


  var initial;
  try {
    initial = get_context_global(context, first);
  } catch (ex) {
    resp(ex, "err");
    return;
  }

  var ptr = traverse_obj(initial, path);


  console.log(ptr);
  resp(ptr);
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
    if (res === undefined) {
      resp(null, "undefined");
    } else {
      resp(res);
    }
    return;
  } catch (ex) {
    resp(ex, "err");
    return;
  }

}

