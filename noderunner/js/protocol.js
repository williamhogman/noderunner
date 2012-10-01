(function(){
  "use strict";

  var EventEmitter = require("events").EventEmitter,
  util = require("util");

  var ord = function(s){
    return s.charCodeAt(0);
  }
  
  var messages = {
    // Init messages
    hello: ord("h"),
    challenge: ord("C"),
    auth: ord("a"),
    auth_resp: ord("A"),
    
    // Runtime
    request: ord("r"),
    response: ord("R"),
    event: ord("E")
    
  }

  var generate_challenge = function(secret) {
    return "10";
  }

  var make_responder_fn = function(protocol, reqid) {
    return function(data, type){
      if (data instanceof Error){
        data = {name: data.name, message: data.message}
      }
      var body = {"response_to": reqid, "type": type || "json", "obj": data};
      protocol._send(messages.response, body)
    };
  }
  
  var Protocol = function(connection, secret){
    EventEmitter.call(this);
    this._secret = secret;
    this._con = connection;
    this._con.on("packet", this._on_pck.bind(this))
  };

  util.inherits(Protocol, EventEmitter);

  Protocol.prototype._send = function(type, body){
    this._con.send(type, body);
  };

  Protocol.prototype._auth_resp = function(status) {
      this._send(messages.auth_resp, {status: status});    
  }

  var dispatch = Protocol.prototype._dispatch = {};

  dispatch[messages.request] = function(body) {
    var fn = make_responder_fn(this, body.reqid);
    this.emit(body.action, body.args, fn);
  };

  dispatch[messages.hello] = function(body){
    if(this._secret) {
      this._send(messages.challenge, {challenge: generate_challenge(this.secret)});
    } else {
      this._auth_resp(true);
      this._authed = true;
    }
  };

  dispatch[messages.auth] = function(body) {
    var cor = verify_signature(body.signature, this._secret)
    this._auth_resp(cor);
    this._authed = cor;
  };

  Protocol.prototype._on_pck = function(type, body){
    var fn = this._dispatch[type];
    if(fn) {
      fn.call(this, body);
    } else {
      console.log("no handler for", type);
    }
  };
  
  module.exports = Protocol;
})();
