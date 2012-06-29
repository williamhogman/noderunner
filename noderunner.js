#!/usr/bin/env node
(function(){
    var parent = this;
    var util = require('util');

    // Object for storing things persistently between commands
    var persistent = {};
    // object containing imported modules
    var m = {};

    var stdin = process.openStdin();
    var stdout = process.stdout;

    // send stdout to stderr which we don't care about...
    process.stdout = process.stderr;
    console.log = function() {
         process.stderr.write(util.format.apply(this, arguments) + '\n');
    }

    stdout.setEncoding("utf8");
    stdin.setEncoding("utf8");

    var message_separator = '\0';

    var create_packet = function(obj){
        return JSON.stringify(obj)+message_separator;
    }

    var write_object = function(obj){
        stdout.write(create_packet(obj));
    };

    var traverse_js = function(path) {
        if( typeof path === 'string' ) {
            path = path.split(".");
        }
        start = eval(path.shift());
        return path.reduce(function(obj,part){
            return obj[part];
        },start);
    }

    var callable_by_name = function(path) {
        var obj = traverse_js(path);
        
        if(obj.apply == null) {
            throw new Error("Is not callable");
        }

        if ( typeof path === 'string') {
            path = path.split(".");
        }

        var lp = path.concat();
        lp.splice(path.length - 1,1);
        
        var  par = traverse_js(lp);

        return function(args) {
            return obj.apply(par,args);
        };
    };

    var command_table = {
        "echo": function(data) { return data },
        "eval": function(data) {
            var wrapper = function() {
                return eval(data);
            }
            return wrapper.apply({});
        },
        "get": function(data) {
            return traverse_js(data);
        },
        "require": function(data) {
            if(typeof data == "string") {
                m[data] = require(data);
                return true;
            } else {
                var md = require(data[1]);
                m[data[0]] = md;
                return true;
            }
            return false;
        },
        "call": function(data) {
            var ret = callable_by_name(data.path)(data.args);
            if(ret == null) {
                return {$: "returned_null", value: null}
            }
            return ret;
        },
        "eval_async": function(callback,errback,data) {
            // Compile
            var fn = new Function(["nr_cb","nr_eb"],data);
            fn.apply({},[callback,errback]);
        },
        "call_async": function(callback,errback,data) {
            var fn = callable_by_name(data.path);
            fn([callback,errback].concat(data.args));
        }
    }

    var run_command = function(obj){
        var cmd_id = obj['id'] || null;
        try {
            if(!obj.kind) {
                throw new Error("Missing required parameter kind");
            }
            var is_async = obj.kind.indexOf("async") != -1
            if(!is_async) {
                write_object({resp_to: cmd_id, data: command_table[obj.kind](obj.data) });
            } else {
                command_table[obj.kind](function(){
                    var rtn = [].concat(arguments);
                    write_object({resp_to: cmd_id, data: rtn});
                }, function(){
                    var rtn = [].concat(arguments);
                    write_object({resp_to: cmd_id, err: rtn});
                },obj.data);
            }
            

        } catch (e) {
            try {
                write_object({resp_to: cmd_id, err: {"message": e.message,"kind": e.name}});
            } catch (ee) {

                write_object({resp_to: cmd_id, err: ee});
            }

        }
    }

    var input_buffer = ""
    stdin.on('data', function(chunk) {
        if (chunk.indexOf(message_separator) != -1){
            var cmds = (input_buffer + chunk).split(message_separator);
            input_buffer = cmds.splice(cmds.length - 1,1)[0];
            cmds.map(JSON.parse).map(run_command);
        } else {
            input_buffer += chunk
        }
    });




    write_object({status: 'ready'});

})();
