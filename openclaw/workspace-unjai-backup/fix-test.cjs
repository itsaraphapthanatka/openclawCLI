const { Pinecone } = require('@pinecone-database/pinecone');
require('dotenv').config();

async function fixTest() {
  const pc = new Pinecone({ 
    apiKey: process.env.PINECONE_API_KEY 
  });
  
  const index = pc.index('aunjai-knowledge');
  
  // Create 384 random values
  const values = [];
  for (let i = 0; i < 384; i++) {
    values.push((Math.random() * 2) - 1); // -1 to 1
  }
  
  // Build record
  const record = {
    id: 'test-' + Date.now(),
    values: values,
    metadata: {
      text: 'Test content',
      source: 'test-file'
    }
  };
  
  console.log('Upserting record:', record.id);
  console.log('Values count:', record.values.length);
  console.log('First 5 values:', record.values.slice(0, 5));
  
  try {
    const result = await index.upsert([record]);
    console.log('✅ Success:', result);
    
    const stats = await index.describeIndexStats();
    console.log('📊 Total records:', stats.totalRecordCount);
    
  } catch (err) {
    console.error('❌ Error:', err.message);
  }
}

fixTest();
