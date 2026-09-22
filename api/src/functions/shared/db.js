const { CosmosClient } = require('@azure/cosmos');

// Centralized Cosmos client + container for the Stott exam app.
//
// This REUSES the same Cosmos DB account as Classroom-survivors (val-esl-db)
// but points at a DEDICATED container (StottUsers) so Stott logins can never
// disturb Classroom-survivors data. DB/container are env-overridable.
let _client = null;
let _container = null;

function getClient() {
    if (!_client) {
        _client = new CosmosClient({
            endpoint: process.env.COSMOS_ENDPOINT,
            key: process.env.COSMOS_KEY,
        });
    }
    return _client;
}

function getContainer() {
    if (!_container) {
        const dbName = process.env.COSMOS_DB_NAME || 'Val-EslApp';
        const containerName = process.env.COSMOS_CONTAINER_NAME || 'StottUsers';
        _container = getClient().database(dbName).container(containerName);
    }
    return _container;
}

module.exports = { getContainer, getClient };
