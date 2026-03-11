#!/usr/bin/env node
/**
 * Import memory files to Pinecone - No API key needed!
 */

const { Pinecone } = require('@pinecone-database/pinecone');
const { readFileSync } = require('fs');
require('dotenv').config();

// Simple hash-based embedding (384 dimensions)
function simpleEmbedding(text, dim = 384) {
  const vector = new Array(dim).fill(0);
  
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    vector[i % dim] += (char % 100) / 100;
  }
  
  // Normalize
  const magnitude = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0));
  return vector.map(v => v / (magnitude || 1));
}

// Split text by character count
function chunkText(text, maxSize = 600) {
  const chunks = [];
  for (let i = 0; i < text.length; i += maxSize) {
    const chunk = text.slice(i, i + maxSize).trim();
    if (chunk.length > 50) {
      chunks.push(chunk);
    }
  }
  return chunks;
}

// Import files to Pinecone
async function importFiles() {
  const pc = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });
  const index = pc.index('aunjai-knowledge');
  
  const files = [
    'SOUL.md',
    'IDENTITY.md', 
    'AGENTS.md',
    'USER.md',
    'TOOLS.md',
    'BOOTSTRAP.md',
    'HEARTBEAT.md',
    'MEMORY.md'
  ];
  
  let totalRecords = 0;
  
  for (const filename of files) {
    try {
      console.log(`\n📖 Processing ${filename}...`);
      const content = readFileSync(`./${filename}`, 'utf-8');
      console.log(`  📄 File size: ${content.length} chars`);
      
      // Split into chunks
      const chunks = chunkText(content, 600);
      console.log(`  📦 Created ${chunks.length} chunks`);
      
      if (chunks.length === 0) {
        console.log(`  ⚠️ No valid chunks`);
        continue;
      }
      
      for (let i = 0; i < chunks.length; i++) {
        const chunk = chunks[i];
        const id = `${filename.replace('.md', '')}-${i}`;
        
        const embedding = simpleEmbedding(chunk, 384);
        
        await index.upsert([{
          id,
          values: embedding,
          metadata: {
            text: chunk.substring(0, 1000),
            source: filename,
            chunkIndex: i,
            timestamp: new Date().toISOString(),
          }
        }]);
        
        totalRecords++;
        process.stdout.write(`  ✅ Saved: ${totalRecords} records\r`);
      }
      
      console.log(`  📊 Done: ${chunks.length} chunks from ${filename}`);
      
    } catch (error) {
      console.error(`  ❌ Error with ${filename}:`, error.message);
    }
  }
  
  console.log(`\n🎉 Import complete! Total: ${totalRecords} records`);
  
  const stats = await index.describeIndexStats();
  console.log(`📊 Index now has ${stats.totalRecordCount} records`);
  
  // Test search
  if (totalRecords > 0) {
    console.log('\n🔍 Testing search with "dashboard"...');
    const testQuery = simpleEmbedding('dashboard', 384);
    const results = await index.query({
      vector: testQuery,
      topK: 3,
      includeMetadata: true,
    });
    
    console.log('Top 3 results:');
    results.matches.forEach((m, i) => {
      console.log(`${i+1}. [${m.id}] Score: ${m.score.toFixed(3)}`);
      console.log(`   ${m.metadata.text.substring(0, 80)}...`);
    });
  }
}

importFiles().catch(console.error);
