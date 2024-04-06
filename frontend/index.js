// Variables
const FRAME_RATE = 10;
const MOTION_RATE = 1.25;
const MAX_SPEED = 3000;
const MAX_DISTANCE = 200;
const BALL_COLOURS = [ 
  "WHITE",
  "YELLOW",
  "BLUE",
  "RED",
  "PURPLE",
  "ORANGE",
  "GREEN",
  "BROWN",
  "BLACK",
  "LIGHTYELLOW",
  "LIGHTBLUE",
  "PINK",             // no LIGHTRED
  "MEDIUMPURPLE",     // no LIGHTPURPLE
  "LIGHTSALMON",      // no LIGHTORANGE
  "LIGHTGREEN",
  "SANDYBROWN",       // no LIGHTBROWN 
];
let clicked = false;
let current;
let mousePos = { x: 0, y: 0 };
let p1, p2, game;

$(document).ready(async function() {
  $("#table").load("empty.svg", function(){
    handleLine();
    for (let i = 1; i < 16; i++) {
      let ele = `<li class="ball-${i}" style="background: ${BALL_COLOURS[i]}; 
      min-width: 20px; min-height: 20px; border-radius: 10px;"></li>`;
      $("#balls").append(ele);
      if (i == 8) {
        $("#balls").append(`<li>|</li>`);
        $("#balls").append(ele);
      } 
    }
  });
});

// Event listener for our shot
$(document).on("mousedown", async function(event){
  if ($(event.target).is($("#cue"))) {
    clicked = true;
    $("#canvas").addClass("clicked");
    handleLine();
  } else if (clicked) {
    clicked = false;
    $("#canvas").removeClass("clicked");
    // Send post request with our information
    let vel = getVelocity()
    let velString = JSON.stringify({ x: vel.x , y: vel.y })
    res = await fetch("api/table/shoot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": velString.length 
      },
      body: velString
    });
    data = await res.json()
    if (!data.svg) return; // Segment function failed

    // Handle all related tasks
    setTimeout(() => {
      $("#p1").html(stringPlayer(p1, data.current, data.low));
      $("#p2").html(stringPlayer(p2, data.current, data.low));
      for (const name of data.balls) {
        if (name != "ball-0") $(`.${name}`).each((i, ele) => $(ele).addClass("hide-vis"));
      }
    }, data.elapsed * 1000);
    handleAnimation(data);
    // handleAnimation(data);
    if (!data.ongoing) {
      // Game over
      setTimeout(() => {
        $("#display").text(`${data.current} has won!`);
        $("#over-menu").removeClass("hide");
      }, data.elapsed * 1000);
    }
    handleLine();
  }
})

// Toggle new game menu
function toggleNew() {
  $("#new-menu").toggleClass("hide");
}

// Toggle hide
function toggleHide(ele, e) {
  if (e.target == ele) $(ele).toggleClass("hide");
}

// Start a new game
async function startGame(e) {
  e.stopPropagation();
  p1 = $("#p1-name").val()
  p2 = $("#p2-name").val()
  game = $("#game-name").val()
  
  if (p1 == "" || p2 == "" || game == "" || p1 == p2) return
  body = JSON.stringify({game: game, p1: p1, p2: p2})
  res = await fetch("api/table/new", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Content-Length": body.length
    },
    body: body
  });
  data = await res.json();
  $("#table").load(data.svg, function(){
    $("#new-menu").addClass("hide");
    $("#p1").html(stringPlayer(p1, data.current, data.low));
    $("#p2").html(stringPlayer(p2, data.current, data.low));
    $("#balls").children().each((i, ele) => $(ele).removeClass("hide-vis"))
  })
}

// Helper function to get full string representation of a player
function stringPlayer(player, current, low) {
  string = player;
  if (low) {
    string += low == player ? " [LOW]" : " [HIGH]";
  }
  string += current == player ? '&nbsp;<span style="font-weight: bold;">[TURN]</span>' : "";
  return string
}

// Helper event listeners
$(window).on("resize", function() {
  handleLine();
});

$(document).on("mousemove", function(event) {
  mousePos.x = event.clientX;
  mousePos.y = event.clientY;
  handleLine();
});

// Helper function to handle an SVG animation for each shot
function handleAnimation(data) {
  $("#table").load(data.svg, function(){
    for (var i = 0; i < data.frames.length; i++) {
      let frame = data.frames[i];
      let delay = i * FRAME_RATE;
      let ele = $(`#${frame}`);
      if (i != 0) ele.delay(delay).queue(() => ele.addClass("active"));
      else ele.addClass("active");
      
      // Keep last frame as the new frame
      if (i != data.frames.length - 1) {
        setTimeout(() => {
          ele.removeClass("active");
        }, delay + FRAME_RATE * MOTION_RATE);
      }
    }
  });
}

// Helper function to draw the line for our shot
function handleLine() {
  if (!$("#cue").get(0)) return;
  let pos = getOffset($("#cue").get(0));
  let offset = normalize(pos);
  let ctx = $("#canvas").get(0).getContext("2d");

  // Maintaining our canvas width with the viewport
  ctx.canvas.width = window.innerWidth;
  ctx.canvas.height = window.innerHeight;
  
  // Styling our line
  ctx.beginPath();
  let percent = Math.abs(pos.top - offset.y) / MAX_DISTANCE * 200 + Math.abs(pos.left - offset.x) / MAX_DISTANCE * 200;
  ctx.strokeStyle = `rgba(${percent}, 0, 0, ${clicked ? '1' : '0'})`;
  ctx.lineWidth = 3;
  ctx.lineCap = "round";
  ctx.moveTo(pos.left, pos.top);
  ctx.lineTo(offset.x, offset.y);
  ctx.stroke();
}

// Helper function to normalize line
function normalize(pos) {
  let dx = mousePos.x - pos.left;
  let dy = mousePos.y - pos.top;  
  let angle = Math.atan2(dy, dx);
  let max = { x: pos.left + MAX_DISTANCE * Math.cos(angle), y: pos.top + MAX_DISTANCE * Math.sin(angle) };
  return {
    x: Math.abs(dx) < Math.abs(max.x - pos.left) ? mousePos.x : max.x,
    y: Math.abs(dy) < Math.abs(max.y - pos.top) ? mousePos.y : max.y,
    max: { x: max.x, y: max.y }
  }
}

// Helper function to get the velocity of our shot on release
function getVelocity() {
  let pos = getOffset($("#cue").get(0));
  let offset = normalize(pos);
  return {
    x: (pos.top - offset.y) / MAX_DISTANCE * MAX_SPEED,
    y: -(pos.left - offset.x) / MAX_DISTANCE * MAX_SPEED
  }
}

// Helper function to get the position of any element on the document 
function getOffset(el) {
  const rect = el.getBoundingClientRect();
  return {
    left: rect.left + rect.width / 2 + window.scrollX,
    top: rect.top + rect.height / 2 + window.scrollY
  };
}