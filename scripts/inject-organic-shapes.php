<?php
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

$header_id = 15;
$header_data_raw = get_post_meta($header_id, '_elementor_data', true);
$header_data = is_string($header_data_raw) ? json_decode($header_data_raw, true) : $header_data_raw;

$shapes = '<style>.header-organic-shapes{position:absolute;top:0;left:0;width:100%;height:200%;overflow:hidden;z-index:0;pointer-events:none}.blob{position:absolute;border-radius:50%;filter:blur(60px);opacity:0.15;animation:blob-morph 25s ease-in-out infinite}.blob-1{width:400px;height:400px;background:linear-gradient(135deg,#5B2E7F 0%,#3D1B5D 100%);top:-150px;left:-100px}.blob-2{width:350px;height:350px;background:linear-gradient(135deg,#F5A623 0%,#FF8C42 100%);top:-50px;right:-120px;animation-delay:10s}.blob-3{width:280px;height:280px;background:linear-gradient(135deg,#3EAAA0 0%,#6B8E23 100%);bottom:-80px;left:40%;animation-delay:17s}@keyframes blob-morph{0%,100%{border-radius:60% 40% 30% 70%/60% 30% 70% 40%;transform:translate(0,0) rotate(0deg)}25%{border-radius:30% 60% 70% 40%/50% 60% 30% 60%;transform:translate(30px,20px) rotate(90deg)}50%{border-radius:50% 60% 30% 60%/30% 50% 70% 40%;transform:translate(-20px,30px) rotate(180deg)}75%{border-radius:60% 40% 60% 40%/70% 30% 50% 60%;transform:translate(20px,-10px) rotate(270deg)}}</style><div class="header-organic-shapes"><div class="blob blob-1"></div><div class="blob blob-2"></div><div class="blob blob-3"></div></div>';

$widget = array(
    'id' => 'shp' . time(),
    'elType' => 'widget',
    'widgetType' => 'html',
    'settings' => array('html' => $shapes)
);

array_unshift($header_data[0]['elements'][0]['elements'], $widget);
update_post_meta($header_id, '_elementor_data', wp_json_encode($header_data));

// Footer
$footer_id = 16;
$footer_data_raw = get_post_meta($footer_id, '_elementor_data', true);
$footer_data = is_string($footer_data_raw) ? json_decode($footer_data_raw, true) : $footer_data_raw;

$footer_shapes = '<style>.footer-organic-shapes{position:absolute;bottom:0;left:0;width:100%;height:150%;overflow:hidden;z-index:0;pointer-events:none}.footer-blob{position:absolute;border-radius:50%;filter:blur(80px);opacity:0.2;animation:footer-blob-morph 30s ease-in-out infinite}.footer-blob-1{width:450px;height:450px;background:linear-gradient(135deg,#3D1B5D 0%,#5B2E7F 100%);bottom:-200px;left:-150px}.footer-blob-2{width:380px;height:380px;background:linear-gradient(135deg,#FF8C42 0%,#F5A623 100%);bottom:-180px;right:10%;animation-delay:12s}.footer-blob-3{width:320px;height:320px;background:linear-gradient(135deg,#6B8E23 0%,#3EAAA0 100%);top:-100px;right:-100px;animation-delay:20s}@keyframes footer-blob-morph{0%,100%{border-radius:55% 45% 35% 65%/55% 35% 65% 45%;transform:translate(0,0) rotate(0deg) scale(1)}33%{border-radius:35% 65% 65% 35%/45% 65% 35% 55%;transform:translate(-25px,35px) rotate(120deg) scale(1.1)}66%{border-radius:65% 35% 55% 45%/35% 55% 45% 65%;transform:translate(35px,-25px) rotate(240deg) scale(0.95)}}</style><div class="footer-organic-shapes"><div class="footer-blob footer-blob-1"></div><div class="footer-blob footer-blob-2"></div><div class="footer-blob footer-blob-3"></div></div>';

$footer_widget = array(
    'id' => 'fshp' . time(),
    'elType' => 'widget',
    'widgetType' => 'html',
    'settings' => array('html' => $footer_shapes)
);

array_unshift($footer_data[0]['elements'][0]['elements'], $footer_widget);
update_post_meta($footer_id, '_elementor_data', wp_json_encode($footer_data));

// Clear Elementor cache
if (class_exists('\Elementor\Plugin')) {
    \Elementor\Plugin::$instance->files_manager->clear_cache();
}

echo "Organic shapes injected successfully!\n";
echo "Header ID: $header_id\n";
echo "Footer ID: $footer_id\n";
?>
