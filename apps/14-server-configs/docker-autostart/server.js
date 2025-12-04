const express = require('express');
const { exec, execSync } = require('child_process');
const fs = require('fs');
const http = require('http');

const app = express();
const config = JSON.parse(fs.readFileSync('/opt/docker-autostart/config.json', 'utf8'));

// Track last access time per service (key = host)
const lastAccess = {};

// Estimated startup times per service type (seconds)
const STARTUP_ESTIMATES = {
  'whisper': 30,
  'whisperx': 30,
  'tika': 20,
  'wordpress': 25,
  'strapi': 20,
  'streamlit': 15,
  'dashy': 10,
  'mkdocs': 5,
  'nextcloud': 20,
  'memvid': 15,
  'ragflow': 45,
  'rag-anything': 20,
  'default': 30
};

// Check if containers are running using docker ps
function areContainersRunning(containers) {
  try {
    for (const containerName of containers) {
      const output = execSync(`docker ps -qf name=^${containerName}$ -f status=running`, {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'ignore']
      });
      if (output.trim().length > 0) {
        return true; // At least one container running
      }
    }
    return false;
  } catch (error) {
    return false;
  }
}

// Get service status
function getServiceStatus(service) {
  const isRunning = areContainersRunning(service.containers);
  const lastAccessTime = lastAccess[service.host];

  let status = 'stopped';
  let idleTime = null;

  if (isRunning) {
    status = 'running';
    if (lastAccessTime) {
      idleTime = Math.floor((Date.now() - lastAccessTime) / 1000);
    }
  }

  return {
    name: service.name,
    status: status,
    containers: service.containers,
    idleTime: idleTime,
    blocking: service.blocking || false
  };
}

// Estimate startup time based on service name
function getEstimatedStartupTime(serviceName) {
  const name = serviceName.toLowerCase();

  if (name.includes('whisper')) return STARTUP_ESTIMATES.whisper;
  if (name.includes('tika')) return STARTUP_ESTIMATES.tika;
  if (name.includes('wordpress') || name.includes('solidar') || name.includes('clemence')) {
    return STARTUP_ESTIMATES.wordpress;
  }
  if (name.includes('strapi') || name.includes('cristina')) return STARTUP_ESTIMATES.strapi;
  if (name.includes('dashboard') || name.includes('sharepoint')) return STARTUP_ESTIMATES.streamlit;
  if (name.includes('dashy')) return STARTUP_ESTIMATES.dashy;
  if (name.includes('mkdocs') || name.includes('docs')) return STARTUP_ESTIMATES.mkdocs;
  if (name.includes('nextcloud')) return STARTUP_ESTIMATES.nextcloud;
  if (name.includes('memvid')) return STARTUP_ESTIMATES.memvid;
  if (name.includes('ragflow')) return STARTUP_ESTIMATES.ragflow;
  if (name.includes('rag-anything')) return STARTUP_ESTIMATES['rag-anything'];

  return STARTUP_ESTIMATES.default;
}

// Start containers
function startContainers(composeDir, serviceName, composeFile) {
  console.log(`[${new Date().toISOString()}] 🔄 Starting containers for ${serviceName}...`);

  // Use docker-compose up -d --no-recreate to start containers (creates them if they don't exist)
  const composeFileArg = composeFile ? `-f ${composeFile}` : '';
  const command = `cd ${composeDir} && docker-compose ${composeFileArg} up -d --no-recreate`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`[${new Date().toISOString()}] ❌ Failed to start ${serviceName}: ${error.message}`);
      console.error(`[${new Date().toISOString()}] Command: ${command}`);
      return;
    }
    console.log(`[${new Date().toISOString()}] ✅ ${serviceName} started`);
  });
}

// Stop containers
function stopContainers(composeDir, serviceName) {
  console.log(`[${new Date().toISOString()}] 🛑 Stopping containers for ${serviceName}...`);
  exec(`cd ${composeDir} && docker-compose stop`, (error, stdout, stderr) => {
    if (error) {
      console.error(`[${new Date().toISOString()}] ❌ Failed to stop ${serviceName}: ${error.message}`);
      return;
    }
    console.log(`[${new Date().toISOString()}] 🛑 ${serviceName} stopped`);
  });
}

// Proxy request to container
function proxyToService(req, res, port, serviceName) {
  const options = {
    hostname: '127.0.0.1',
    port: port,
    path: req.url,
    method: req.method,
    headers: req.headers
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on('error', (error) => {
    console.error(`[${new Date().toISOString()}] Proxy error for ${serviceName}:`, error.message);

    // Estimate startup time and send Retry-After header
    const retryAfter = getEstimatedStartupTime(serviceName);

    res.status(503)
       .header('Retry-After', retryAfter.toString())
       .header('X-Service-Status', 'starting')
       .header('X-Service-Name', serviceName)
       .send(`Service Starting - Retry after ${retryAfter}s`);
  });

  if (req.method === 'POST' || req.method === 'PUT') {
    req.pipe(proxyReq);
  } else {
    proxyReq.end();
  }
}

// Wait for containers to be ready with retries
async function waitForReady(containers, maxRetries = 30, intervalMs = 1000) {
  for (let i = 0; i < maxRetries; i++) {
    if (areContainersRunning(containers)) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2s more after "running"
      return true;
    }
    await new Promise(resolve => setTimeout(resolve, intervalMs));
  }
  return false;
}

// Load waiting page template
const themes = {
  'hacker-terminal': fs.readFileSync('/opt/docker-autostart/themes/hacker-terminal.html', 'utf8'),
  'ghost': fs.readFileSync('/opt/docker-autostart/themes/ghost.html', 'utf8'),
  'matrix': fs.readFileSync('/opt/docker-autostart/themes/matrix.html', 'utf8'),
  'shuffle': fs.readFileSync('/opt/docker-autostart/themes/shuffle.html', 'utf8'),
};

// =============================================================================
// API ENDPOINTS - Health check and service status
// =============================================================================

// Health check endpoint for specific service by hostname
app.get('/health/:hostname', (req, res) => {
  const hostname = req.params.hostname;
  const service = config.services[hostname];

  if (!service) {
    return res.status(404).json({
      error: 'Service not found',
      hostname: hostname
    });
  }

  const isRunning = areContainersRunning(service.containers);
  const estimatedStartup = getEstimatedStartupTime(service.name);

  if (isRunning) {
    res.status(200).json({
      status: 'ready',
      service: service.name,
      hostname: hostname,
      containers: service.containers
    });
  } else {
    res.status(503)
       .header('Retry-After', estimatedStartup.toString())
       .json({
         status: 'starting',
         service: service.name,
         hostname: hostname,
         estimatedTime: estimatedStartup,
         containers: service.containers
       });
  }
});

// List all services and their status
app.get('/api/services', (req, res) => {
  const services = Object.keys(config.services).map(host => {
    const service = config.services[host];
    return {
      hostname: host,
      ...getServiceStatus({ ...service, host })
    };
  });

  res.json({
    totalServices: services.length,
    idleTimeout: config.idleTimeout,
    services: services
  });
});

// Main request handler
app.use((req, res) => {
  const host = req.headers.host;
  const service = config.services[host];

  if (!service) {
    return res.status(404).send('Service not configured');
  }

  // Update last access time
  lastAccess[host] = Date.now();

  const isRunning = areContainersRunning(service.containers);

  console.log(`[${new Date().toISOString()}] ${service.name} - isRunning: ${isRunning}`);

  if (isRunning) {
    // Containers running, proxy to service
    return proxyToService(req, res, service.proxyPort, service.name);
  }

  // Containers stopped, start them
  startContainers(service.composeDir, service.name, service.composeFile);

  if (service.mode === 'async' || service.async) {
    // ASYNC mode (for APIs): return 202 immediately with retry info
    const retryAfter = getEstimatedStartupTime(service.name);
    res.status(202)
       .header('Retry-After', retryAfter.toString())
       .json({
         status: 'starting',
         message: `Service ${service.name} is starting. Please retry in ${retryAfter} seconds.`,
         service: service.name,
         estimatedTime: retryAfter,
         retryAfter: retryAfter,
         healthCheckUrl: `/health/${host}`
       });
  } else if (service.blocking) {
    // Blocking mode: wait for containers to be ready (legacy, not recommended for APIs)
    waitForReady(service.containers).then((ready) => {
      if (ready) {
        proxyToService(req, res, service.proxyPort, service.name);
      } else {
        const retryAfter = getEstimatedStartupTime(service.name);
        res.status(504)
           .header('Retry-After', retryAfter.toString())
           .send('Service startup timeout');
      }
    });
  } else {
    // Dynamic mode: show waiting page with theme
    const theme = themes[service.theme] || themes['hacker-terminal'];
    const html = theme
      .replace(/{{SERVICE_NAME}}/g, service.name)
      .replace(/{{DISPLAY_NAME}}/g, service.name);

    res.setHeader('Content-Type', 'text/html');
    res.send(html);
  }
});

// Idle checker - runs every minute
setInterval(() => {
  const now = Date.now();
  const timeoutMs = config.idleTimeout * 1000;

  Object.keys(config.services).forEach((host) => {
    const service = config.services[host];
    const lastAccessTime = lastAccess[host];

    if (!lastAccessTime) {
      // Never accessed, skip
      return;
    }

    const idleTimeMs = now - lastAccessTime;
    const idleMinutes = Math.floor(idleTimeMs / 60000);

    if (idleTimeMs > timeoutMs) {
      const isRunning = areContainersRunning(service.containers);
      if (isRunning) {
        console.log(`[${new Date().toISOString()}] Service ${service.name} idle for ${idleMinutes}min`);
        stopContainers(service.composeDir, service.name);
        delete lastAccess[host]; // Reset access time
      }
    }
  });
}, 60000);

// Start server
const port = config.port || 8890;
app.listen(port, () => {
  console.log(`🚀 Docker Auto-Start server running on port ${port}`);
  console.log(`⏱️  Idle timeout: ${config.idleTimeout}s (${Math.floor(config.idleTimeout / 60)}min)`);
  console.log(`📋 Services configured: ${Object.keys(config.services).length}`);
  console.log(`\n📍 Health check: http://localhost:${port}/health/:hostname`);
  console.log(`📍 Services API: http://localhost:${port}/api/services`);
});
