const { Pinecone } = require('@pinecone-database/pinecone');
require('dotenv').config();

async function debug() {
  const pc = new Pinecone({ 
    apiKey: process.env.PINECONE_API_KEY 
  });
  
  // List indexes
  const indexes = await pc.listIndexes();
  console.log('Indexes:', indexes.indexes.map(i => i.name));
  
  // Use the index
  const index = pc.index('aunjai-knowledge');
  
  // Try upsert with explicit namespace
  const records = [{
    id: 'test-001',
    values: new Array(384).fill(0.1),
    metadata: { text: 'Hello', source: 'test' }
  }];
  
  console.log('Records to upsert:', JSON.stringify(records, null, 2));
  
  try {
    await index.upsert(records, { namespace: '' });
    console.log('✅ Success!');
  } catch (err) {
    console.error('❌ Error:', err.message);
    console.error('Full error:', err);
  }
}

debug();
