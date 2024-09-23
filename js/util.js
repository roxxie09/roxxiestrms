<<<<<<< HEAD
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  if (match) {
      return match[2];
  }
  return '';
}
function formatTimestamp(timestamp) {
  const date = new Date(timestamp * 1000);
  const options = {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true
  };
  const formattedDate = new Intl.DateTimeFormat("en-US", options).format(date);
  const dayWithOrdinal = addOrdinalSuffix(date.getDate());
  const formattedDateWithOrdinal = formattedDate.replace(/(\d+)/, dayWithOrdinal);
  return formattedDateWithOrdinal;
}
function addOrdinalSuffix(day) {
  if (day >= 11 && day <= 13) {
      return `${day}th`;
  }
  switch (day % 10) {
      case 1:
      return `${day}st`;
      case 2:
      return `${day}nd`;
      case 3:
      return `${day}rd`;
      default:
      return `${day}th`;
  }
}
function createCenterTopToast(content, type = 'info', options = {}) {
  var existingToasts = document.querySelectorAll('.toast');
  existingToasts.forEach(function (toast) {
      toast.remove();
  });

  var toastElement = document.createElement('div');
  toastElement.classList.add('toast');
  toastElement.classList.add('position-absolute', 'top-0', 'start-50', 'translate-middle-x');
  toastElement.style.marginTop = '50px'; // Adjust the top margin for the desired gap
  toastElement.setAttribute('role', 'alert');
  toastElement.setAttribute('aria-live', 'assertive');
  toastElement.setAttribute('aria-atomic', 'true');

  if (type === 'success') {
      toastElement.classList.add('bg-success', 'text-white');
  } else if (type === 'danger') {
      toastElement.classList.add('bg-danger', 'text-white');
  }

  var toastBody = document.createElement('div');
  toastBody.classList.add('toast-body');
  toastBody.innerHTML = content;

  toastElement.appendChild(toastBody);

  var toastHeader = document.createElement('div');
  toastHeader.classList.add('toast-header', 'text-white', 'border-0');

  if (type === 'success') {
      toastHeader.classList.add('bg-success');
  } else if (type === 'danger') {
      toastHeader.classList.add('bg-danger');
  }
  var strongTag = document.createElement('strong');
  strongTag.classList.add('me-auto');
  strongTag.textContent = options.name || 'Notification';

  var closeButton = document.createElement('button');
  closeButton.classList.add('btn-close', 'btn-close-white', 'ms-2');
  closeButton.setAttribute('type', 'button');
  closeButton.setAttribute('data-bs-dismiss', 'toast');
  closeButton.setAttribute('aria-label', 'Close');

  toastHeader.appendChild(strongTag);
  toastHeader.appendChild(closeButton);
  toastElement.insertBefore(toastHeader, toastElement.firstChild);
  var toastInstance = new bootstrap.Toast(toastElement, {
      autohide: false
  });
  toastInstance.show();
  document.body.appendChild(toastElement);
  return 0;
}

async function checkLiveStatus(playlist) {
  try {
      const response = await fetch(playlist);
      if (response.ok) {
          console.log('Playlist is valid. Status code: 200');
          return true;
      } else {
          console.log(`Playlist is not valid. Status code: ${response.status}`);
          return false;
      }
  } catch (error) {
      console.error('Error checking playlist validity:', error);
      return false;
  }
}
function processStream(data) {
  if (data.success == false) {
      alert("Stream failed - this may be due to an incorrect ID or privacy settings. Tell a member of staff if this keeps happening. Press OK to go home.")
      location.href="/"
      return
  }
  data = data.data
  link = data.m3u8
  poster = data.poster

  document.getElementById("title").innerText = data.name

  if(data.source_type=='playlist') {
      player = jwplayer("player").setup({
          width: "100%",
          height: "720",
          title: data.name,
          image: poster,
          aspectratio: "16:9",
          responsive: true,
          repeat: true,
          displayTitle: true,
          playlist: [ { file: link } ],
          cast: {}
      });
  }
  if(data.source_type=='json') { // use custom jwplayer json to setup player.
      player = jwplayer("player").setup({
          width: "100%",
          height: "720",
          title: data.name,
          image: poster,
          aspectratio: "16:9",
          responsive: true,
          repeat: true,
          displayTitle: true,
          playlist: JSON.parse(data.source),
          cast: {}
      });
      createCenterTopToast(`{customjsondisclaimer}`, "danger", {"name":"{attention}"});
      setTimeout(function() {
          var existingToasts = document.querySelectorAll('.toast');
          existingToasts.forEach(function (toast) {
              toast.remove();
          });
      }, 5000);
  }
  player.addButton("/assets/download.svg", "Report an issue", function(err, result){$('#report_issue').modal('toggle')}, "report_btn")
  player.addButton("/assets/theatre.svg", "{theatre}", function(err, result){layoutswitch()}, "layout_btn")
  if(data.clipping) {
      player.addButton("/assets/clip.svg", "Clip", function(err, result){$('#clipui').modal('toggle')}, "clip_btn")
  }
  try { player.play(); } catch (err) { console.log("no autoplay permissions") }
  player.on('error', function(event) {
      const last_error = event.code;
      document.cookie = 'fs_last_error='+event.code+'; expires=Mon, 18 Jan 2038 12:00:00 UTC; path=/';
      if (event.code === 232404) {
          createCenterTopToast(`This event has not started yet or has ended.<br><br>Starts: ${formatTimestamp(data.start_timestamp)}<br>Ends: ${formatTimestamp(data.end_timestamp)}<br><br>The stream will begin playing automatically once it has started.`, "secondary", {"name":"Event information"});
          console.log("error code 232404");
          player.load({file: "https://stacked.b-cdn.net/prod-output/video_SWIZL6OT4mu7cO/b811ee10-c93f-492f-a937-48b9a27c73d8.m3u8"});
          // player.load({file: "/static/preset-1.mp4"});
          player.play();
      }
      if (event.code === 232011) {
        createCenterTopToast(`This event has not started yet or has ended.<br><br>Starts: ${formatTimestamp(data.start_timestamp)}<br>Ends: ${formatTimestamp(data.end_timestamp)}<br><br>The stream will begin playing automatically once it has started.`, "secondary", {"name":"Event information"});
        console.log("error code 232011");
        player.load({file: "https://stacked.b-cdn.net/prod-output/video_SWIZL6OT4mu7cO/b811ee10-c93f-492f-a937-48b9a27c73d8.m3u8"});
        // player.load({file: "/static/preset-1.mp4"});
        player.play();
      }
      if (event.code === 233011) {
        createCenterTopToast(`This event has not started yet or has ended.<br><br>Starts: ${formatTimestamp(data.start_timestamp)}<br>Ends: ${formatTimestamp(data.end_timestamp)}<br><br>The stream will begin playing automatically once it has started.`, "secondary", {"name":"Event information"});
        console.log("error code 233011");
        player.load({file: "https://stacked.b-cdn.net/prod-output/video_SWIZL6OT4mu7cO/b811ee10-c93f-492f-a937-48b9a27c73d8.m3u8"});
        // player.load({file: "/static/preset-1.mp4"});
        player.play();
      }
      if(event.code === 334002) {
          console.log("error code 334002 - attempting recovery...")
          player.load({file: link});
          player.play();
      }
      const playlistintcheck = setInterval(function() {
          (async () => {
              if(data.source_type=='json') { clearInterval(playlistintcheck); return true; }
              const stat = await checkLiveStatus(link);
              if(stat) {
                  var existingToasts = document.querySelectorAll('.toast'); // clear event information toast once stream becomes available.
                  existingToasts.forEach(function (toast) {
                      toast.remove();
                  });
                  clearInterval(playlistintcheck);
                  player.load({file: link});
                  player.play();
              }
          })();
      }, 5000);
  });
  player.on('warning', function(event) {
      if(event.code === 334002) {
          console.log("error code 334002 - attempting recovery...")
          player.load({file: link});
          player.play();
      }
  });
}

function layout(type) {
  if(type=="theatre") {
      $("#container").css("max-width", "100%");
      $("#container").removeClass("mt-4");
      $("#chat-col").css("padding-left","6px");
      $("#video-col").css("padding-right","6px");
      $("#tc-message-cont").css("height","38.6vw");
      //$('body').css('background-color', '#0A0A0A');
      $('body').css('background-color', '#000000');
      $("#chat-col").css("width","20.2%");
      $("#title").hide();
      $("#viewersparent").hide();
      $("footer").removeClass("mt-5").addClass("mt-0")
  }
  if(type=="normal") {
      $("#container").css("max-width", "1542px");
      $("#container").addClass("mt-4");
      $("#chat-col").css("padding-left","12px");
      $("#video-col").css("padding-right","12px");
      $("#tc-message-cont").css("height","27.8vw");
      $('body').css('background-color', '#0e0e0e');
      $("#chat-col").css("width","25%");
      $("#title").show();
      $("#viewersparent").show();
      $("footer").removeClass("mt-0").addClass("mt-5")
  }
}
function layoutswitch() {
  tmo = getCookie('theatre_mode');
  if(tmo!=='true') {
      document.cookie = "theatre_mode=true; expires=Tue, 01 Jan 2030 12:00:00 UTC";
      layout('theatre');
  } else {
      document.cookie = "theatre_mode=false; expires=Tue, 01 Jan 2030 12:00:00 UTC";
      layout("normal");
  }
=======
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  if (match) {
      return match[2];
  }
  return '';
}
function formatTimestamp(timestamp) {
  const date = new Date(timestamp * 1000);
  const options = {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true
  };
  const formattedDate = new Intl.DateTimeFormat("en-US", options).format(date);
  const dayWithOrdinal = addOrdinalSuffix(date.getDate());
  const formattedDateWithOrdinal = formattedDate.replace(/(\d+)/, dayWithOrdinal);
  return formattedDateWithOrdinal;
}
function addOrdinalSuffix(day) {
  if (day >= 11 && day <= 13) {
      return `${day}th`;
  }
  switch (day % 10) {
      case 1:
      return `${day}st`;
      case 2:
      return `${day}nd`;
      case 3:
      return `${day}rd`;
      default:
      return `${day}th`;
  }
}
function createCenterTopToast(content, type = 'info', options = {}) {
  var existingToasts = document.querySelectorAll('.toast');
  existingToasts.forEach(function (toast) {
      toast.remove();
  });

  var toastElement = document.createElement('div');
  toastElement.classList.add('toast');
  toastElement.classList.add('position-absolute', 'top-0', 'start-50', 'translate-middle-x');
  toastElement.style.marginTop = '50px'; // Adjust the top margin for the desired gap
  toastElement.setAttribute('role', 'alert');
  toastElement.setAttribute('aria-live', 'assertive');
  toastElement.setAttribute('aria-atomic', 'true');

  if (type === 'success') {
      toastElement.classList.add('bg-success', 'text-white');
  } else if (type === 'danger') {
      toastElement.classList.add('bg-danger', 'text-white');
  }

  var toastBody = document.createElement('div');
  toastBody.classList.add('toast-body');
  toastBody.innerHTML = content;

  toastElement.appendChild(toastBody);

  var toastHeader = document.createElement('div');
  toastHeader.classList.add('toast-header', 'text-white', 'border-0');

  if (type === 'success') {
      toastHeader.classList.add('bg-success');
  } else if (type === 'danger') {
      toastHeader.classList.add('bg-danger');
  }
  var strongTag = document.createElement('strong');
  strongTag.classList.add('me-auto');
  strongTag.textContent = options.name || 'Notification';

  var closeButton = document.createElement('button');
  closeButton.classList.add('btn-close', 'btn-close-white', 'ms-2');
  closeButton.setAttribute('type', 'button');
  closeButton.setAttribute('data-bs-dismiss', 'toast');
  closeButton.setAttribute('aria-label', 'Close');

  toastHeader.appendChild(strongTag);
  toastHeader.appendChild(closeButton);
  toastElement.insertBefore(toastHeader, toastElement.firstChild);
  var toastInstance = new bootstrap.Toast(toastElement, {
      autohide: false
  });
  toastInstance.show();
  document.body.appendChild(toastElement);
  return 0;
}

async function checkLiveStatus(playlist) {
  try {
      const response = await fetch(playlist);
      if (response.ok) {
          console.log('Playlist is valid. Status code: 200');
          return true;
      } else {
          console.log(`Playlist is not valid. Status code: ${response.status}`);
          return false;
      }
  } catch (error) {
      console.error('Error checking playlist validity:', error);
      return false;
  }
}
function processStream(data) {
  if (data.success == false) {
      alert("Stream failed - this may be due to an incorrect ID or privacy settings. Tell a member of staff if this keeps happening. Press OK to go home.")
      location.href="/"
      return
  }
  data = data.data
  link = data.m3u8
  poster = data.poster

  document.getElementById("title").innerText = data.name

  if(data.source_type=='playlist') {
      player = jwplayer("player").setup({
          width: "100%",
          height: "720",
          title: data.name,
          image: poster,
          aspectratio: "16:9",
          responsive: true,
          repeat: true,
          displayTitle: true,
          playlist: [ { file: link } ],
          cast: {}
      });
  }
  if(data.source_type=='json') { // use custom jwplayer json to setup player.
      player = jwplayer("player").setup({
          width: "100%",
          height: "720",
          title: data.name,
          image: poster,
          aspectratio: "16:9",
          responsive: true,
          repeat: true,
          displayTitle: true,
          playlist: JSON.parse(data.source),
          cast: {}
      });
      createCenterTopToast(`{customjsondisclaimer}`, "danger", {"name":"{attention}"});
      setTimeout(function() {
          var existingToasts = document.querySelectorAll('.toast');
          existingToasts.forEach(function (toast) {
              toast.remove();
          });
      }, 5000);
  }
  player.addButton("/assets/download.svg", "Report an issue", function(err, result){$('#report_issue').modal('toggle')}, "report_btn")
  player.addButton("/assets/theatre.svg", "{theatre}", function(err, result){layoutswitch()}, "layout_btn")
  if(data.clipping) {
      player.addButton("/assets/clip.svg", "Clip", function(err, result){$('#clipui').modal('toggle')}, "clip_btn")
  }
  try { player.play(); } catch (err) { console.log("no autoplay permissions") }
  player.on('error', function(event) {
      const last_error = event.code;
      document.cookie = 'fs_last_error='+event.code+'; expires=Mon, 18 Jan 2038 12:00:00 UTC; path=/';
      if (event.code === 232404) {
          createCenterTopToast(`This event has not started yet or has ended.<br><br>Starts: ${formatTimestamp(data.start_timestamp)}<br>Ends: ${formatTimestamp(data.end_timestamp)}<br><br>The stream will begin playing automatically once it has started.`, "secondary", {"name":"Event information"});
          console.log("error code 232404");
          player.load({file: "https://stacked.b-cdn.net/prod-output/video_SWIZL6OT4mu7cO/b811ee10-c93f-492f-a937-48b9a27c73d8.m3u8"});
          // player.load({file: "/static/preset-1.mp4"});
          player.play();
      }
      if (event.code === 232011) {
        createCenterTopToast(`This event has not started yet or has ended.<br><br>Starts: ${formatTimestamp(data.start_timestamp)}<br>Ends: ${formatTimestamp(data.end_timestamp)}<br><br>The stream will begin playing automatically once it has started.`, "secondary", {"name":"Event information"});
        console.log("error code 232011");
        player.load({file: "https://stacked.b-cdn.net/prod-output/video_SWIZL6OT4mu7cO/b811ee10-c93f-492f-a937-48b9a27c73d8.m3u8"});
        // player.load({file: "/static/preset-1.mp4"});
        player.play();
      }
      if (event.code === 233011) {
        createCenterTopToast(`This event has not started yet or has ended.<br><br>Starts: ${formatTimestamp(data.start_timestamp)}<br>Ends: ${formatTimestamp(data.end_timestamp)}<br><br>The stream will begin playing automatically once it has started.`, "secondary", {"name":"Event information"});
        console.log("error code 233011");
        player.load({file: "https://stacked.b-cdn.net/prod-output/video_SWIZL6OT4mu7cO/b811ee10-c93f-492f-a937-48b9a27c73d8.m3u8"});
        // player.load({file: "/static/preset-1.mp4"});
        player.play();
      }
      if(event.code === 334002) {
          console.log("error code 334002 - attempting recovery...")
          player.load({file: link});
          player.play();
      }
      const playlistintcheck = setInterval(function() {
          (async () => {
              if(data.source_type=='json') { clearInterval(playlistintcheck); return true; }
              const stat = await checkLiveStatus(link);
              if(stat) {
                  var existingToasts = document.querySelectorAll('.toast'); // clear event information toast once stream becomes available.
                  existingToasts.forEach(function (toast) {
                      toast.remove();
                  });
                  clearInterval(playlistintcheck);
                  player.load({file: link});
                  player.play();
              }
          })();
      }, 5000);
  });
  player.on('warning', function(event) {
      if(event.code === 334002) {
          console.log("error code 334002 - attempting recovery...")
          player.load({file: link});
          player.play();
      }
  });
}

function layout(type) {
  if(type=="theatre") {
      $("#container").css("max-width", "100%");
      $("#container").removeClass("mt-4");
      $("#chat-col").css("padding-left","6px");
      $("#video-col").css("padding-right","6px");
      $("#tc-message-cont").css("height","38.6vw");
      //$('body').css('background-color', '#0A0A0A');
      $('body').css('background-color', '#000000');
      $("#chat-col").css("width","20.2%");
      $("#title").hide();
      $("#viewersparent").hide();
      $("footer").removeClass("mt-5").addClass("mt-0")
  }
  if(type=="normal") {
      $("#container").css("max-width", "1542px");
      $("#container").addClass("mt-4");
      $("#chat-col").css("padding-left","12px");
      $("#video-col").css("padding-right","12px");
      $("#tc-message-cont").css("height","27.8vw");
      $('body').css('background-color', '#0e0e0e');
      $("#chat-col").css("width","25%");
      $("#title").show();
      $("#viewersparent").show();
      $("footer").removeClass("mt-0").addClass("mt-5")
  }
}
function layoutswitch() {
  tmo = getCookie('theatre_mode');
  if(tmo!=='true') {
      document.cookie = "theatre_mode=true; expires=Tue, 01 Jan 2030 12:00:00 UTC";
      layout('theatre');
  } else {
      document.cookie = "theatre_mode=false; expires=Tue, 01 Jan 2030 12:00:00 UTC";
      layout("normal");
  }
>>>>>>> 5abea60f8c5fe20faefb8efd059987d45cd8ca9c
}