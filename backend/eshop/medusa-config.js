const path = require('path');
const dockerSecret = require('docker-secret');


// Loads ENV variables
dotenv.config({ path: path.resolve(__dirname, '..', '..', '.env') });


// Gets Docker Secret
function getSecret(secretName) {
  try {
    return dockerSecret(secretName) || process.env[secretName];
  } catch (err) {
    console.error(`Error reading secret ${secretName}:`, err);
    return null;
  }
}


// CORS for Medusa Admin and Medusa Client
const ADMIN_CORS = process.env.ADMIN_CORS;
const STORE_CORS = process.env.STORE_CORS;


// Sets up DTB connection using Secret
const DATABASE_URL = `postgres://${getSecret('db_eshop_admin')}:${getSecret('db_eshop_password')}@myhost:5432/db_eshop`;


// Sets up Redis URL
const REDIS_URL = `redis://${getSecret('redis_password')}@redis:6379/1`;


// Plug-ins definition
const plugins = [
  `medusa-fulfillment-manual`,
  `medusa-payment-manual`,
  {
    resolve: `@medusajs/file-local`,
    options: {
      upload_dir: "uploads",
    },
  },
  {
    resolve: "@medusajs/admin",
    /** @type {import('@medusajs/admin').PluginOptions} */
    options: {
      autoRebuild: true,
      develop: {
        open: process.env.OPEN_BROWSER !== "false",
      },
    },
  },
];


// Modules definition
const modules = {
  eventBus: {
    resolve: "@medusajs/event-bus-redis",
    options: {
      redisUrl: REDIS_URL
    }
  },
  cacheService: {
    resolve: "@medusajs/cache-redis",
    options: {
      redisUrl: REDIS_URL
    }
  },
};

// Project configuration
/** @type {import('@medusajs/medusa').ConfigModule["projectConfig"]} */
const projectConfig = {
  jwt_secret: getSecret('jwt_secret'),
  cookie_secret: getSecret('cookie_secret'),
  store_cors: STORE_CORS,
  database_url: DATABASE_URL,
  admin_cors: ADMIN_CORS,
  redis_url: REDIS_URL
};

/** @type {import('@medusajs/medusa').ConfigModule} */
module.exports = {
  projectConfig,
  plugins,
  modules,
};
