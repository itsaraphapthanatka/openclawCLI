// Check what's inside aunjai-knowledge index
import { Pinecone } from '@pinecone-database/pinecone';
import * as dotenv from 'dotenv';

dotenv.config();

async function checkKnowledgeBase() {
  const pc = new Pinecone({
    apiKey: process.env.PINECONE_API_KEY || '',
  });
  
  const indexName = 'aunjai-knowledge';
  const index = pc.index(indexName);
  
  console.log(`🔍 Checking index: ${indexName}\n`);
  
  // Get index stats
  const stats = await index.describeIndexStats();
  console.log('📊 Index Stats:');
  console.log(`  - Dimension: ${stats.dimension}`);
  console.log(`  - Total Records: ${stats.totalRecordCount}`);
  console.log(`  - Namespaces: ${Object.keys(stats.namespaces || {}).join(', ') || 'default'}`);
  
  // Query with a dummy vector to get some records
  // Using 384 dimensions (from the stats we saw earlier)
  console.log('\n📚 Sample Records:');
  const dummyVector = new Array(384).fill(0).map(() => Math.random() - 0.5);
  
  try {
    const results = await index.query({
      vector: dummyVector,
      topK: 10,
      includeMetadata: true,
    });
    
    if (results.matches && results.matches.length > 0) {
      results.matches.forEach((match, i) => {
        console.log(`\n[${i + 1}] ID: ${match.id}`);
        console.log(`    Score: ${match.score?.toFixed(4)}`);
        console.log(`    Metadata:`, JSON.stringify(match.metadata, null, 2));
      });
    } else {
      console.log('  (No records found with random query)');
    }
    
    // Try to query with zero vector to get any records
    console.log('\n📖 Trying to fetch all records...');
    const zeroVector = new Array(384).fill(0);
    const allResults = await index.query({
      vector: zeroVector,
      topK: 100,
      includeMetadata: true,
    });
    
    if (allResults.matches && allResults.matches.length > 0) {
      console.log(`Found ${allResults.matches.length} records:\n`);
      allResults.matches.forEach((match, i) => {
        const text = match.metadata?.text || match.metadata?.content || JSON.stringify(match.metadata);
        console.log(`${i + 1}. [${match.id}] ${text?.substring(0, 100)}...`);
      });
    }
    
  } catch (error) {
    console.error('❌ Error querying:', error.message);
  }
}

checkKnowledgeBase().catch(console.error);
