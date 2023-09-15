<!DOCTYPE html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="main.css">
    <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
    <title>TSMC Hackathon Group7</title>
</head>

<script src="https://unpkg.com/aos@next/dist/aos.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<!-- <script>
    function srchData(){
        srch=document.getElementById("srchInput").value
        console.log('srch: ',srch)
    }
</script> -->

<body>
    <div id="headDiv" class="cntrDiv">
        <h2>即時影像</h2>
    </div>
    <div class="cntrDiv" id='videoDiv'>
        <iframe width="560" height="315" src="https://www.youtube.com/embed/zoYxtoY-IJk"
            title="YouTube video player" frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
        </iframe>
    </div>
    <div class='cntrDiv' id="srchDiv">
         <div>
            <h3>Search</h3>
            <select id="srchInput" onchange="srchData()">
                <option>----</option>
                <option>Within 10 mins</option>
                <option>Within 1 hr</option>
                <option>Within 1 day</option>
                <option>Within 1 month</option>
            </select>
         </div>
         <div id='srch'></div>
    </div>
    
    <div class='cntrDiv'>
        <button class="button-23" role="button" onclick="showData()">Show All Data</button>
    </div>
    <div id='data'></div>
</body>

<script>
    AOS.init();
</script>
<script>
    function showData(){
        jQuery.ajax({
            url: "printDBdata.php", 
            data:{
            },
            type: "POST",
            success: function(data) {
            document.getElementById("data").innerHTML=data;
            },
            error: function() {
            console.log('ERROR')
            }
        });
    }
    function srchData(){
        srch=document.getElementById("srchInput").value
        console.log(srch)
        jQuery.ajax({
            url: "srchDBdata.php", 
            data:{
                srch: srch
            },
            type: "POST",
            success: function(data) {
                document.getElementById("srch").innerHTML=data;
            },
            error: function() {
                console.log('ERROR')
            }
        });
    }
</script>

