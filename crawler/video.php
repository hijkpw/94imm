<?php

function getConn() {
    $dbuser = "填写数据库用户名";
    $dbpass = "填写数据库密码";
    $conn = new PDO("mysql:host=localhost;port=3306;dbname=填写数据库名;", $dbuser, $dbpass, array(
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_PERSISTENT => true,
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_general_ci"
    ));
    return $conn;
}
$opts = array(
  'http'=>array(
    'method'=>"GET",
    'header'=>"Accept-language: en\r\n" .
              "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36\r\n"
  )
);

$context = stream_context_create($opts);

# 从https://sp.nico.run 下载视频
function getVideoUrl() {
    global $context;
    $url = "https://sp.nico.run/video.php?_t=" . bin2hex(openssl_random_pseudo_bytes(10));
    @file_get_contents($url, false, $context);
    $videoUrl = "";
	foreach ($http_response_header as $value) {
        $vals = explode(":", $value);
        if (strtolower(trim($vals[0])) == "location") {
            $videoUrl = $vals[1] . ":" . $vals[2];
            echo "video url: ", $videoUrl, PHP_EOL;
            break;
        }
    }

    return trim($videoUrl);
}

$conn = getConn();
function checkExists($videoUrl) {
    global $conn;
    $sts = $conn->query("SELECT * FROM images_video where v_name='$videoUrl'");
    $res = $sts->fetchAll();
    return count($res) > 0;
}


$length = 1000;
for ($i = 0; $i < $length; ++ $i) {
    $videoUrl = getVideoUrl();

    if ($videoUrl != "") {
        $filename = basename($videoUrl);
        echo "视频文件名： $filename", PHP_EOL;
        if (checkExists($videoUrl)) {
            echo "视频： $videoUrl 已采集", PHP_EOL;
        } else {
            $content = @file_get_contents($videoUrl, false, $context);
            if ($content && file_put_contents("../static/videos/$filename", $content)) {
                $conn->exec("INSERT INTO images_video(url,user_id,date_time,v_name,v_path,source) VALUE('/static/videos/$filename', 12345, now(), '$videoUrl', 'url', '互联网')");
                echo "视频： $videoUrl 下载成功", PHP_EOL;
            } else {
                echo "视频： $videoUrl 下载失败", PHP_EOL;
            }
        }
    }

    sleep(5);
}
