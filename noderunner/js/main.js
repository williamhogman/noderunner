(function(){
  console.log("This is noderunner!")
  var net = require("net");
  var fd, filename;

  try {
    fd = parseInt(process.argv[2])
  } catch (Error) {
    filename = process.argv[2] || "/tmp/noderunner.socket";
  }
  
  var secret = process.argv[3] || null;

  if (secret == "__NO_AUTH__") {
    secret = null;
    console.log("no auth mode");
  }

  var Connection = require("./connection");
  var Protocol = require("./protocol");
  
  var mk_socket = function() {
    if (fd) {
      console.log("using passed in fd!")
      return new net.Socket({fd: fd, type: "unix"})    
    } else {
      console.log("using path to named socket")
      var socket = new net.Socket({type: "unix"})
      socket.connect(filename);
      return socket;
    }
  }


  var run = function(){
    var sck = mk_socket();
    var c = new Connection(sck);
    var p = new Protocol(c, secret);
    p.on("lefoo", function(data, resp){
      console.log("yay");
      resp("booyeah!");
    });
  };

  run();
})();

