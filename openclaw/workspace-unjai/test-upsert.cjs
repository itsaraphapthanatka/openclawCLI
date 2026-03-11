const { Pinecone } = require('@pinecone-database/pinecone');
require('dotenv').config();

async function test() {
  const pc = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });
  const index = pc.index('aunjai-knowledge');
  
  // Test single upsert
  const testEmbedding = new Array(384).fill(0).map(() => Math.random());
  
  console.log('Testing upsert...');
  console.log('Vector length:', testEmbedding.length);
  
  try {
    await index.upsert([{
      id: 'test-001',
      values: testEmbedding,
      metadata: { text: 'Test record', source: 'test' }
    }]);
    console.log('✅ Upsert successful!');
    
    // Check stats
    const stats = await index.describeIndexStats();
    console.log('Records:', stats.totalRecordCount);
    
  } catch (err) {
    console.error('❌ Error:', err.message);
    console.log('Type of values:', typeof testEmbedding);
    console.log('Is array:', Array.isArray(testEmbedding));
  }
}

test();
