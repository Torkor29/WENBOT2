<?php
/*
 * Configuration WordPress pour l'intégration du Trading Analyzer
 * À ajouter dans wp-config.php ou dans un fichier d'initialisation de plugin
 */

// Configuration CORS pour l'API
define('ALLOW_CORS', true);
if (defined('ALLOW_CORS') && ALLOW_CORS) {
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type');
}

// Configuration de l'API
define('TRADING_ANALYZER_API_URL', 'https://trading-analyzer-api.onrender.com');
define('TRADING_ANALYZER_UPLOAD_MAX_SIZE', 16777216); // 16MB

// Fonction pour vérifier la taille des fichiers
function ta_check_upload_size($file) {
    if ($file['size'] > TRADING_ANALYZER_UPLOAD_MAX_SIZE) {
        wp_die('File is too large. Maximum size is ' . size_format(TRADING_ANALYZER_UPLOAD_MAX_SIZE));
    }
    return $file;
}
add_filter('wp_handle_upload_prefilter', 'ta_check_upload_size');

// Ajouter les scripts nécessaires
function ta_enqueue_analyzer_scripts() {
    if (is_page('trading-analyzer')) {
        wp_enqueue_style('ta-styles', plugins_url('assets/css/styles.css', __FILE__));
        wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js', array(), null, true);
        wp_enqueue_script('ta-scripts', plugins_url('assets/js/main.js', __FILE__), array('chart-js'), null, true);
        
        // Passer les variables à JavaScript
        wp_localize_script('ta-scripts', 'taConfig', array(
            'apiUrl' => TRADING_ANALYZER_API_URL,
            'maxUploadSize' => TRADING_ANALYZER_UPLOAD_MAX_SIZE,
            'nonce' => wp_create_nonce('ta-upload-nonce')
        ));
    }
}
add_action('wp_enqueue_scripts', 'ta_enqueue_analyzer_scripts');

// Ajouter le menu dans l'administration
function ta_admin_menu() {
    add_menu_page(
        'Trading Analyzer',
        'Trading Analyzer',
        'manage_options',
        'trading-analyzer',
        'ta_admin_page',
        'dashicons-chart-line',
        30
    );
}
add_action('admin_menu', 'ta_admin_menu');

// Page d'administration
function ta_admin_page() {
    ?>
    <div class="wrap">
        <h1>Trading Analyzer Configuration</h1>
        <form method="post" action="options.php">
            <?php
            settings_fields('ta_options');
            do_settings_sections('ta_options');
            ?>
            <table class="form-table">
                <tr>
                    <th scope="row">API URL</th>
                    <td>
                        <input type="text" name="ta_api_url" 
                               value="<?php echo esc_attr(get_option('ta_api_url')); ?>" 
                               class="regular-text">
                    </td>
                </tr>
                <tr>
                    <th scope="row">Max Upload Size (bytes)</th>
                    <td>
                        <input type="number" name="ta_max_upload_size" 
                               value="<?php echo esc_attr(get_option('ta_max_upload_size', 16777216)); ?>" 
                               class="regular-text">
                    </td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

// Enregistrer les options
function ta_register_settings() {
    register_setting('ta_options', 'ta_api_url');
    register_setting('ta_options', 'ta_max_upload_size');
}
add_action('admin_init', 'ta_register_settings');

// Shortcode pour afficher l'analyseur
function ta_display_analyzer($atts) {
    ob_start();
    include(plugin_dir_path(__FILE__) . 'templates/analyzer.php');
    return ob_get_clean();
}
add_shortcode('trading_analyzer', 'ta_display_analyzer');

// Fonction de nettoyage des fichiers temporaires
function ta_cleanup_temp_files() {
    $upload_dir = wp_upload_dir();
    $ta_temp_dir = $upload_dir['basedir'] . '/ta-temp';
    
    if (is_dir($ta_temp_dir)) {
        $files = glob($ta_temp_dir . '/*');
        $now = time();
        
        foreach ($files as $file) {
            if (is_file($file)) {
                if ($now - filemtime($file) >= 24 * 3600) { // 24 heures
                    unlink($file);
                }
            }
        }
    }
}
add_action('wp_scheduled_delete', 'ta_cleanup_temp_files');

// Fonction de sécurité pour les uploads
function ta_secure_upload($file) {
    $allowed_types = array('application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    
    if (!in_array($file['type'], $allowed_types)) {
        wp_die('File type not allowed');
    }
    
    return $file;
}
add_filter('wp_handle_upload_prefilter', 'ta_secure_upload'); 