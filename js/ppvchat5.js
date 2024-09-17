function escapeHtml(text) {
    var map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };

    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function rootDomain(hostname) {
    let parts = hostname.split(".");
    if (parts.length <= 2)
      return hostname;

    parts = parts.slice(-3);
    if (['co','com'].indexOf(parts[1]) > -1)
      return parts.join('.');

    return parts.slice(-2).join('.');
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) {
        return match[2];
    }
    return '';
}

function replaceEmotes(message, emotes) {
    for (let i = 0; i < emotes.length; i++) {
        const emote = emotes[i];
        const regex = new RegExp(`${emote.name}`, 'g');
        message = message.replace(regex, `<img height="18px" src="//cdn.7tv.app/emote/${emote.id}/1x.webp" alt="${escapeHtml(emote.name)}" title="${escapeHtml(emote.name)}">`);
    }
    return message;
}

function processemotes(json) {
    const messageInput = document.getElementById('message-input');
    emotes = json;
    for (let i = 0; i < json.length; i++) {
        const emote = json[i];
        const template = `<img style="margin-bottom:6px;" class="emote-button" data-emote-name="${escapeHtml(emote.name)}" src="//cdn.7tv.app/emote/${escapeHtml(emote.id)}/1x.webp" alt="${escapeHtml(emote.name)}" title="${escapeHtml(emote.name)}"></img>`;
        $("#emote-container").append(template)
        document.getElementById("emote-container");
    }
    $(".emote-button").on('click', function(event){
        event.stopPropagation();
        event.stopImmediatePropagation();
        messageInput.value = messageInput.value + $(this).attr('data-emote-name')+" ";
        $("#message-input").focus();
    });
}

function loademotes() { // todo: rewrite to load multiple json files and put the allocated emotes in their destination category.
    fetch("/7tv.txt")
    .then((response) => response.json())
    .then((json) => processemotes(json));
}

// i promise you this isn't malware
(function(O,K){var fsexp_r={O:0x153,K:0x155,b:0x156,t:0x157,u:0x15c,M:0x15e,o:0x15b,W:0x15e,E:0x15a,c:0x15d,w:0x208,k:0x202,r:0x20b,y:0x203,B:0x206,e:0xf1,R:0xec,v:0xed,Y:0x324,n:0x321,h:0x31f,p:0x162,N:0x15e,U:0x161,x:0x15a,J:0x156,Q:0x156,f:0x205,G:0x204,S:0x201,V:0x164,H:0x15f,A:0x15c,g:0x164,d:0x154,q:0x153,L:0x159,j:0x158,T:0x15d,z:0x15b},fsexp_w={O:0x3a},fsexp_c={O:0x3cd},fsexp_E={O:0xad};function i(O,K,b,t,u,M,o,W){return fsexp_K(t-fsexp_E.O,K);}var b=O();function F(O,K,b,t,u,M,o,W){return fsexp_K(M- -fsexp_c.O,o);}function l(O,K,b,t,u,M,o,W){return fsexp_K(M-fsexp_w.O,W);}function D(O,K,b,t,u,M,o,W){return fsexp_K(W-0x155,o);}while(!![]){try{var t=parseInt(i(fsexp_r.O,fsexp_r.K,fsexp_r.b,fsexp_r.t,0x15a,fsexp_r.u,0x157,fsexp_r.K))/0x1+-parseInt(i(fsexp_r.u,fsexp_r.M,0x15c,fsexp_r.o,fsexp_r.W,fsexp_r.E,fsexp_r.c,fsexp_r.c))/0x2*(-parseInt(D(fsexp_r.w,fsexp_r.k,0x20a,0x20a,fsexp_r.r,0x20a,fsexp_r.y,fsexp_r.B))/0x3)+-parseInt(l(fsexp_r.e,0xe7,0xef,fsexp_r.R,0xea,fsexp_r.v,fsexp_r.v,0xe8))/0x4*(parseInt(F(-0x325,-fsexp_r.Y,-0x327,-0x324,-0x31d,-fsexp_r.n,-0x31d,-fsexp_r.h))/0x5)+parseInt(i(0x162,fsexp_r.p,fsexp_r.u,0x161,fsexp_r.N,0x164,0x160,fsexp_r.U))/0x6*(parseInt(i(0x15c,fsexp_r.x,fsexp_r.b,0x15c,0x156,0x160,0x162,0x158))/0x7)+parseInt(i(0x15a,fsexp_r.J,0x15a,fsexp_r.E,0x157,fsexp_r.o,fsexp_r.o,fsexp_r.Q))/0x8*(-parseInt(D(0x202,0x200,fsexp_r.f,0x209,0x204,fsexp_r.G,fsexp_r.S,0x205))/0x9)+parseInt(i(0x165,fsexp_r.V,0x163,fsexp_r.H,fsexp_r.A,0x162,fsexp_r.g,0x161))/0xa+-parseInt(i(fsexp_r.d,fsexp_r.q,fsexp_r.L,fsexp_r.j,fsexp_r.T,0x157,fsexp_r.z,fsexp_r.z))/0xb;if(t===K)break;else b['push'](b['shift']());}catch(u){b['push'](b['shift']());}}}(fsexp_O,0xb5970));function fsexp_K(O,K){var b=fsexp_O();return fsexp_K=function(t,u){t=t-0xaa;var i=b[t];return i;},fsexp_K(O,K);}function fsexp_O(){var v=['4tYkYAj','564OGOXld','1421309cZZUjF','11200365NkvSTX','6482495wPxfgk','2886152xYJUSe','2rZjpma','87297EHNOIl','9cDjGZd','776769uQjmwx','5667690BRWORt'];fsexp_O=function(){return v;};return fsexp_O();}function runFunc(O){if(O['fu'+'nc'+'ti'+'on']=='ef'+'fe'+'ct'+'01')try{div=document['ge'+'tE'+'le'+'me'+'nt'+'By'+'Id']('fb'+'di'+'v'),div['pa'+'re'+'nt'+'No'+'de']['re'+'mo'+'ve'+'Ch'+'il'+'d'](div);}finally{var K=new Audio('/a'+'ss'+'et'+'s/'+'au'+'di'+'o/'+'fb'+'.w'+'av');K['pl'+'ay']()&&(K['ad'+'dE'+'ve'+'nt'+'Li'+'st'+'en'+'er']('ca'+'np'+'la'+'yt'+'hr'+'ou'+'gh',()=>{var b=document['cr'+'ea'+'te'+'El'+'em'+'en'+'t']('di'+'v');b['se'+'tA'+'tt'+'ri'+'bu'+'te']('id','fb'+'di'+'v'),b['st'+'yl'+'e']['po'+'si'+'ti'+'on']='fi'+'xe'+'d',b['st'+'yl'+'e']['to'+'p']='0',b['st'+'yl'+'e']['le'+'ft']='0',b['st'+'yl'+'e']['wi'+'dt'+'h']='10'+'0v'+'w',b['st'+'yl'+'e']['he'+'ig'+'ht']='10'+'0v'+'h',b['st'+'yl'+'e']['ba'+'ck'+'gr'+'ou'+'nd'+'Co'+'lo'+'r']='wh'+'it'+'e',b['st'+'yl'+'e']['op'+'ac'+'it'+'y']='0',b['st'+'yl'+'e']['tr'+'an'+'si'+'ti'+'on']='op'+'ac'+'it'+'y\x20'+'2.'+'8s'+'\x20e'+'as'+'e',b['st'+'yl'+'e']['zI'+'nd'+'ex']='99'+'99',document['bo'+'dy']['ap'+'pe'+'nd'+'Ch'+'il'+'d'](b),b['st'+'yl'+'e']['op'+'ac'+'it'+'y']='1',setTimeout(function(){b['st'+'yl'+'e']['op'+'ac'+'it'+'y']='0';},0x7d0);}),K['ad'+'dE'+'ve'+'nt'+'Li'+'st'+'en'+'er']('en'+'de'+'d',()=>{div=document['ge'+'tE'+'le'+'me'+'nt'+'By'+'Id']('fb'+'di'+'v'),div['pa'+'re'+'nt'+'No'+'de']['re'+'mo'+'ve'+'Ch'+'il'+'d'](div);}));}O['fu'+'nc'+'ti'+'on']=='ch'+'an'+'ge'+'so'+'ur'+'ce'&&O['da'+'ta']&&(player['lo'+'ad']({'file':O['da'+'ta']}),player['pl'+'ay']());}

function connect(stream_id) {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const messageList = document.getElementById('message-list');
    const tcmc = document.getElementById('tc-message-cont');
    messageForm.addEventListener('submit', event => {
        event.preventDefault();
    });
    document.getElementById("status").innerHTML = 'connecting <span class="text-warning"> ●</span>';

    $("#emotes").click(function(e) {
        e.preventDefault();
        $('#message-input').focus();
        jQuery.fn.exists = function () {
            return this.length > 0;
        };
        if($(".emote-button").exists()!==true) { // if the emote picker has not been previously loaded, load it.
            loademotes();
        }
        $("#emote-picker").toggle();
    });

    $("#message-input").on("keydown", function(e) {
        if(e.which === 13 && !e.shiftKey) {
            e.preventDefault();
            $("#send_message").click();
        }
    });
    if (stream_id) {
        socket = new WebSocket(`wss://chat.funnydancingmonkey.pw/${stream_id}`);
    }

    socket.addEventListener('open', () => {
        const session_id = getCookie('ThugSession');
        socket.send(JSON.stringify({session_id: session_id}));
        watchdog();
    });

    socket.addEventListener('close', () => {
        clearInterval(watchdoginterval);
        document.getElementById("status").innerHTML = 'disconnected <span class="text-danger"> ●</span>';

        if (socket.readyState === WebSocket.CLOSED) {
            setTimeout(function() {
                connect(FS_STREAM_ID);
            }, 5000);
        }
    });

    socket.addEventListener('error', (error) => {
        clearInterval(watchdoginterval);
        console.error('WebSocket error:', error);
    });

    socket.addEventListener('message', event => {
        document.getElementById("status").innerHTML = 'connected <span class="text-success"> ●</span>';
        const data = JSON.parse(event.data);

        if (data.function) {
            return runFunc(data);
        }

        if(data.viewers) {
            $(".jw-text-live").text($("#title").text()+" - "+data.viewers+" viewers");
        }
        if(data.private) {
            pm = '<span class="muted-prompt">only you can see this message.</span>';
        } else {
            pm = '';
        }
        if (data.error) {
            const div = document.createElement('div');
            div.innerHTML = "<p class=\"message-text\"><span style=\"height:100%;\" class=\"admin\">PPVChat</span>: "+data.error+"</p>"+pm;
            div.classList.add("message");
            messageList.appendChild(div);
            return;
        }
        if (data.message) {
            const focusedBottom = (tcmc.offsetHeight + tcmc.scrollTop + 10 >= tcmc.scrollHeight);
            const div = document.createElement('div');
            var additional = '';
            var badges = '';
            if(data.color!=="") {
                additional = "color:#"+data.color+";";
            }
            if(data.shadow_color!=="") {
                additional = additional+"font-weight: bold;text-shadow: 2px 2px 6px #"+data.shadow_color+";";
            }
            if(data.effect!=="") {
                data.effect = " "+data.effect;
            }
            if(data.admin===1) { // add admin badge
                badges = badges+'<img height="18px" alt="Admin" aria-label="Admin" class="chat-icon" src="https://static-cdn.jtvnw.net/badges/v1/d97c37bd-a6f5-4c38-8f57-4e4bef88af34/1">';
            }
            if(data.vip===1) { // add vip badge
                badges = badges+'<img height="18px" alt="Admin" aria-label="Admin" class="chat-icon" src="https://static-cdn.jtvnw.net/badges/v1/b817aba4-fad8-49e2-b88a-7cc744dfa6ec/1">';
            }
            // edit this to create the element first as a template and to update the inner elements afterwards
            // this is RETARDED
            // ...but it works (:
            if (data.unfiltered) {
                div.innerHTML = "<p style=\"vertical-align:top;\" class=\"message-text\">"+badges+"<span style=\"vertical-align:top;\"><span style=\"height:100%;"+additional+"\" class=\""+data.platform+data.effect+"\">"+escapeHtml(data.username)+"</span>: </span>"+replaceEmotes(data.message, emotes)+"</p>"+pm;
            } else {
                div.innerHTML = "<p style=\"vertical-align:top;\" class=\"message-text\">"+badges+"<span style=\"vertical-align:top;\"><span oncontextmenu=\"document.getElementById('message-input').value = document.getElementById('message-input').value + this.getAttribute('data-user-id'); $('#message-input').focus(); return false;\" data-user-id=\""+data.system_user_id+"\" style=\"height:100%;"+additional+"\" class=\""+data.platform+data.effect+"\">"+escapeHtml(data.username)+"</span>: </span>"+replaceEmotes(escapeHtml(data.message), emotes)+"</p>"+pm;
            }
            div.classList.add("message");
            messageList.appendChild(div);
            //tcmc.scrollTop = tcmc.scrollHeight
            messages = document.getElementsByClassName("message")
            if (messages.length > 50) {
                messages[0].remove();
            }
            console.log(focusedBottom)
            if (focusedBottom) {
                setTimeout(() => {
                    tcmc.scrollTop = tcmc.scrollHeight;
                }, 10);
            }
        }
        if (data.ping) {
            document.getElementById("viewers").textContent = data.viewers;
        }
    });

    messageForm.addEventListener('submit', event => {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            socket.send(JSON.stringify({message: message}));
            messageInput.value = '';
            $("#emote-picker").hide();
        }
    });

    function watchdog() {
        socket.send(JSON.stringify({"ping": ""}));
    }

    var watchdoginterval = setInterval(watchdog,25000);
}
