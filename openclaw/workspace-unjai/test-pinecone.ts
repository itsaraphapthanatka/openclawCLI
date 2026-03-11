// Test Pinecone Connection
import { Pinecone } from '@pinecone-database/pinecone';
import * as dotenv from 'dotenv';

dotenv.config();

async function testConnection() {
  try {
    const pc = new Pinecone({
      apiKey: process.env.PINECONE_API_KEY || '',
    });
    
    // List all indexes
    const indexes = await pc.listIndexes();
    console.log('✅ Connected to Pinecone!');
    console.log('📋 Existing indexes:', indexes);
    
    // Create index if not exists
    const indexName = process.env.PINECONE_INDEX_NAME || 'unjai-memory';
    const existingIndex = indexes.indexes?.find(idx => idx.name === indexName);
    
    if (!existingIndex) {
      console.log(`🆕 Creating index: ${indexName}`);
      await pc.createIndex({
        name: indexName,
        dimension: 1536,
        metric: 'cosine',
        spec: {
          serverless: {
            cloud: 'aws',
            region: 'us-east-1'
          }
        }
      });
      console.log(`✅ Index "${indexName}" created!`);
    } else {
      console.log(`✅ Index "${indexName}" already exists`);
    }
    
    // Get index stats
    const index = pc.index(indexName);
    const stats = await index.describeIndexStats();
    console.log('📊 Index stats:', stats);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

testConnection();
