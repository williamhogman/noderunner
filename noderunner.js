#!/usr/bin/env node
(function(){
    var parent = this;

    // Object for storing things persistently between commands
    var persistent = {};

    var stdin = process.openStdin();
    var stdout = process.stdout;

    // send stdout to stderr which we don't care about...
    process.stdout = process.stderr;

    stdout.setEncoding("utf8")
    stdin.setEncoding("utf8")

    var message_separator = '\0';

    var create_packet = function(obj){
        return JSON.stringify(obj)+message_separator;
    }

    var write_object = function(obj){
        stdout.write(create_packet(obj));
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
            data.split(".").reduce(function(obj,a){
                return obj[a];
            },parent);
        }
    }

    var run_command = function(obj){
        var cmd_id = obj['id'] || null;
        try {
            if(!obj.kind) {
                throw "Missing required parameter kind";
            }
            write_object({resp_to: cmd_id, data: command_table[obj.kind](obj.data) });
        } catch (e) {
            write_object({resp_to: cmd_id, err: e});
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
