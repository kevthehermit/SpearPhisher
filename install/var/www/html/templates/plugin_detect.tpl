
<iframe width="0" height="0" tabindex="-1" name="plugin_target" ></iframe>

<script>

function post() {
    path = "http://[[portal_domain]]/plugins"

    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", path);
    form.setAttribute("target", "plugin_target");

    // UID
    var uidField = document.createElement("input");
    uidField.setAttribute("type", "hidden");
    uidField.setAttribute("name", "uid");
    uidField.setAttribute("value", "[[uid]]");
    form.appendChild(uidField);

    // CID
    var cidField = document.createElement("input");
    cidField.setAttribute("type", "hidden");
    cidField.setAttribute("name", "cid");
    cidField.setAttribute("value", "[[c_id]]");
    form.appendChild(cidField);

    // Set delimeter
    PluginDetect.getVersion(".");
    
    // Java Plugin
    var javaField = document.createElement("input");
    javaField.setAttribute("type", "hidden");
    javaField.setAttribute("name", "Java");
    javaField.setAttribute("value", PluginDetect.getVersion("Java"));
    form.appendChild(javaField);
    
    // Flash Plugin
    var flashField = document.createElement("input");
    flashField.setAttribute("type", "hidden");
    flashField.setAttribute("name", "AdobeFlash");
    flashField.setAttribute("value", PluginDetect.getVersion("Flash"));
    form.appendChild(flashField);
    
    // Adobe Plugin
    var pdfField = document.createElement("input");
    pdfField.setAttribute("type", "hidden");
    pdfField.setAttribute("name", "AdobeReader");
    pdfField.setAttribute("value", PluginDetect.getVersion("AdobeReader"));
    form.appendChild(pdfField);

    // Shockwave Plugin
    var shockField = document.createElement("input");
    shockField.setAttribute("type", "hidden");
    shockField.setAttribute("name", "Shockwave");
    shockField.setAttribute("value", PluginDetect.getVersion("Shockwave"));
    form.appendChild(shockField);
    
    // Silverlight Plugin
    var silverField = document.createElement("input");
    silverField.setAttribute("type", "hidden");
    silverField.setAttribute("name", "Silverlight");
    silverField.setAttribute("value", PluginDetect.getVersion("Silverlight"));
    form.appendChild(silverField);

    
    
    document.body.appendChild(form);
    form.submit();
}

PluginDetect.onWindowLoaded(post());





</script>

