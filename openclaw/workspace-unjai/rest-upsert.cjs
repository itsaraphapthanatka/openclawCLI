require('dotenv').config();

async function upsertDirect() {
  const apiKey = process.env.PINECONE_API_KEY;
  const indexName = 'aunjai-knowledge';
  
  // Get index host
  const controlResp = await fetch('https://api.pinecone.io/indexes', {
    headers: { 'Api-Key': apiKey }
  });
  const indexes = await controlResp.json();
  const index = indexes.indexes.find(i => i.name === indexName);
  
  if (!index) {
    console.error('Index not found');
    return;
  }
  
  console.log('Index host:', index.host);
  
  // Prepare vectors
  const values = new Array(384).fill(0).map(() => (Math.random() * 2) - 1);
  
  const body = {
    vectors: [{
      id: 'record-' + Date.now(),
      values: values,
      metadata: {
        text: 'Test from REST API',
        source: 'rest-test'
      }
    }],
    namespace: ''
  };
  
  console.log('Sending upsert...');
  
  const resp = await fetch(`https://${index.host}/vectors/upsert`, {
    method: 'POST',
    headers: {
      'Api-Key': apiKey,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });
  
  if (resp.ok) {
    console.log('✅ Upsert successful!');
    const result = await resp.json();
    console.log('Result:', result);
  } else {
    console.error('❌ Error:', resp.status, await resp.text());
  }
}

upsertDirect().catch(console.error);
