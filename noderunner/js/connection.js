(function(){
  var assert = require("assert"),
  EventEmitter = require("events").EventEmitter,
  util = require("util");

  Connection = function(stream){
    EventEmitter.call(this);
    this.stream = stream;
    
    this.stream.on("data",this._on_data.bind(this));

    this._header_bfr = new Buffer(8);

    this._reset_state();

    this.stream.resume();
  };
  util.inherits(Connection, EventEmitter);
  

  var _parse_header = function(b){
    assert.equal(b.length, 8, "buffer is of the wrong size");

    return { version: b.readUInt8(0, true),
             command: b.readUInt8(1, true),
             //padding x2
             length: b.readUInt32BE(4, true) }
  };

  var parse_body = function(b) {
    return JSON.parse(b.toString("utf8"));
  }

  Connection.prototype._version = 1;
  
  Connection.prototype.send = function(type, body) {
    var body = JSON.stringify(body);
    var len = Buffer.byteLength(body, "utf8");
    var bfr = new Buffer(8 + len);
    bfr.writeUInt8(this._version, 0, true);
    bfr.writeUInt8(type, 1);
    bfr.writeUInt32BE(len, 4);
    bfr.write(body, 8);
    
    this.stream.write(bfr);
  };

  Connection.prototype._reset_state = function() {
    this._ctr = 0;
    this._in_header = true;
  }

  Connection.prototype._alloc_cbuffer = function(n) {
    if (!this._content ||  n != this._content.length) {
      this._content = new Buffer(n);
    }
  }

  Connection.prototype._read_header = function(inp) {
    // How many bytes left to parse
    var rem = inp.length;
    // still in header

    var last = Math.min(inp.length, 8 - this._ctr);
    inp.copy(this._header_bfr, this._ctr, 0, last);

    // Increment 
    this._ctr += last;

    assert(this._ctr <= 8, "header may never be longer than 8 bytes");
    if(this._ctr == 8) {
      this._header = _parse_header(this._header_bfr);
      this._alloc_cbuffer(this._header.length)
      this._in_header = false;
      this._ctr = 0;
    } 
    return inp.length - last;
  };

  Connection.prototype._read_body = function(inp, rem) {
    // First non-read byte
    var first = inp.length - rem;
    // either the entire buffer or enough to fill the command
    var last = Math.min(first + this._header.length, inp.length);
    inp.copy(this._content, this._ctr, first, last);


    this._ctr += last - first;

    assert(this._ctr <= this._content.length);
    if (this._ctr == this._content.length) {
      this.emit("packet", this._header.command, parse_body(this._content))
      this._reset_state();
    }


    return rem - (last - first);
  }
  
  Connection.prototype._on_data = function(inp) {
    var rem = inp.length;
    if (rem > 0 && this._in_header) {
      rem = this._read_header(inp);
    }

    if(rem > 0 && !this._in_header) {
      rem = this._read_body(inp, rem)
    }

    if (rem > 0) {
      // call recursively with the remainder
      this._on_data(inp.slice(inp.length - rem));
    }
  };
  module.exports = Connection;
})();

