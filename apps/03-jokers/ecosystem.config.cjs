module.exports = {
  apps: [{
    name: 'jokers-hockey',
    script: './dist/index.js',
    instances: 1,
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 5000
    },
    env_file: '.env',
    max_memory_restart: '500M',
    error_file: './logs/error.log',
    out_file: './logs/output.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    autorestart: true,
    watch: false,
    // Restart delay en cas d'erreur
    restart_delay: 5000,
    // Nombre max de restarts consécutifs
    max_restarts: 10,
    // Temps minimum entre les restarts
    min_uptime: '10s',
    // Kill timeout
    kill_timeout: 5000,
    // Wait ready
    wait_ready: true,
    listen_timeout: 10000,
    // Monitoring
    pmx: true,
    instance_var: 'INSTANCE_ID'
  }]
}
