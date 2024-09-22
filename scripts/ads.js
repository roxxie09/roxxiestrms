(function() {
    //version 1.0.0

    // Ad configuration object
    var adConfig = {
        "ads_host": "a.pemsrv.com",
        "syndication_host": "s.pemsrv.com",
        "idzone": 5425990,
        "popup_fallback": true,
        "popup_force": false,
        "chrome_enabled": true,
        "new_tab": false,
        "frequency_period": 720,
        "frequency_count": 3,
        "trigger_method": 1,
        "trigger_class": "",
        "trigger_delay": 0,
        "capping_enabled": false,
        "only_inline": false
    };

    // Helper function to load scripts dynamically
    function loadScript(src, callback) {
        var script = document.createElement('script');
        script.async = true;
        script.type = 'application/javascript';
        script.src = src;
        script.onload = callback;
        document.body.appendChild(script);
    }

    // Helper function to insert ad zones
    function insertAd(zoneId, className) {
        var ins = document.createElement('ins');
        ins.className = className;
        ins.setAttribute('data-zoneid', zoneId);
        document.body.appendChild(ins);
        (AdProvider = window.AdProvider || []).push({"serve": {}});
    }

    // Load the necessary scripts and insert the ads
    loadScript('https://a.magsrv.com/ad-provider.js', function() {
        insertAd(5426000, 'eas6a97888e2');  // Ad 1
        insertAd(5426004, 'eas6a97888e6');  // Ad 2
        insertAd(5426008, 'eas6a97888e17'); // Ad 3
    });

    // Load the second ad provider script
    loadScript('https://a.pemsrv.com/ad-provider.js', function() {
        insertAd(5426012, 'eas6a97888e35'); // Ad 4
    });

})();
